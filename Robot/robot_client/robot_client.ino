#include <Servo.h>
#include <NewPing.h>
#include "ESP8266.h"
#include <Wire.h>
#include <HMC5883L.h>
#include <ArduinoJson.h>


/*
Pin e costanti del sonar
*/
//#define TRIGGER_PIN 50
//#define ECHO_PIN 51
//#define MAX_DISTANCE 200

/*
Pin degli infrarossi
*/
#define RIGHT_IR_PIN 22
#define BACK_IR_PIN 26
#define LEFT_IR_PIN 28
#define FRONT_IR_PIN 24
#define FRONT_IR_RIGHT 33
#define FRONT_IR_LEFT 31

/*
Pin per il motore
*/
#define E1 8
#define E2 13
#define I1 9
#define I2 10
#define I3 11
#define I4 12

/*
Costanti per la connessione con il server
*/
//#define SSID        "Telecom-56943924"
//#define PASSWORD    "lVGtZMVqI4XUQp5AWBcEHkQ7"

#define SSID        "VodafoneMobileWiFi-E3D656"
#define PASSWORD    "2926693643"

/*
Parametri del server
*/
#define SERVER_NAME "192.168.0.100"
#define SERVER_PORT (1931)

/*
Costruttori per gli oggetti
*/
Servo myservo;
//NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
ESP8266 wifi(Serial1, 115200);
HMC5883L compass;

// infrarossi
int IRLeftVal;
int IRFrontVal;
int IRRightVal;
int IRBackVal;
int IRFrontDxVal;
int IRFrontSxVal;
// sonar
//int sonar_value;
// compass
float compass_value;
// Variabile usata per i pacchetti JSON che il robot manda al server

StaticJsonBuffer<256> jsonBuffer;
String datiSensoriali = "{\"sonar\":-1, \"IR_dx\": -1, \"IR_sx\": -1, \"IR_cdx\": -1, \"IR_c\": -1, \"IR_csx\": -1, \"IR_b\": -1, \"buss\": -1}";
JsonObject& root = jsonBuffer.parseObject(datiSensoriali);

void setup(){
  //myservo.attach(6);
  //myservo.write(90);
  pinMode(FRONT_IR_PIN, INPUT);
  pinMode(FRONT_IR_RIGHT, INPUT);
  pinMode(FRONT_IR_LEFT, INPUT);
  pinMode(BACK_IR_PIN, INPUT);
  pinMode(LEFT_IR_PIN, INPUT);
  pinMode(RIGHT_IR_PIN, INPUT);

  pinMode(E1, OUTPUT);
  pinMode(E2, OUTPUT);
  pinMode(I1, OUTPUT);
  pinMode(I2, OUTPUT);
  pinMode(I3, OUTPUT);
  pinMode(I4, OUTPUT);

  Serial.begin(115200);

  wifiSetup();
  compassSetup();
}


void loop(){
  
  createTCPConnection();
  // Mando i dati sensoriali al server
  sendSensorDataToServer();
  // Ricevo la risposta dal server
  char* comandoDaServer = receivingDataTCP();
  analizzaDati(comandoDaServer);
  releaseTCPConnection();
}

/***************************************************************************/
/*
Funzione per mandare i dati al server
*/
void sendSensorDataToServer(){
  Serial.println("Mando i dati al server");
  getSensorsData();
  char dati_sensoriali[170];
  root.printTo(dati_sensoriali, sizeof(dati_sensoriali));
  wifi.send(dati_sensoriali, strlen(dati_sensoriali));
  
}

void getSensorsData(){
  
  //sonar_value = sonar.convert_cm(sonar.ping_median());

  IRLeftVal = digitalRead(LEFT_IR_PIN);
  IRFrontVal = digitalRead(FRONT_IR_PIN);
  IRRightVal = digitalRead(RIGHT_IR_PIN);
  IRBackVal = digitalRead(BACK_IR_PIN);
  IRFrontDxVal = digitalRead(FRONT_IR_RIGHT);
  IRFrontSxVal = digitalRead(FRONT_IR_LEFT);
  
  compass_value = getDegreeFromCompass();

  //root["sonar"] = sonar_value;
  root["sonar"] = -1;
  root["IR_dx"] = IRRightVal;
  root["IR_c"] = IRFrontVal;
  root["IR_b"] = IRBackVal;
  root["IR_sx"] = IRLeftVal;
  root["IR_cdx"] = IRFrontDxVal;
  root["IR_csx"] = IRFrontSxVal;
  root["buss"] = compass_value;
  root.printTo(Serial);
}

/***************************************************************************/
/*
Funzioni per estrapolare i dati mandati dal server
*/
void analizzaDati(char* data){
  
  StaticJsonBuffer<128> jsonStringBuffer;
  JsonObject& jsonString = jsonStringBuffer.parseObject(data);
  if(!jsonString.success()) {
    Serial.println("parseObject() failed");
    return;
  }
  char* azione = jsonString["azione"];
  
  if(strcmp(azione, "rotazione") == 0) {
    moveForward(0, 0);
    float angolo_target = jsonString["angolo_target"];
    int verso = jsonString["verso_rot"]; 
    rotateRobot(verso, angolo_target);
    return;
  }

  if(strcmp(azione, "movimento") == 0){
    int avanti = jsonString["avanti"];
    int indietro = jsonString["indietro"];
    int ruota_sx = jsonString["v_ruota_sx"];
    int ruota_dx = jsonString["v_ruota_dx"];  
    int verso = jsonString["verso"]; 
    float angolo_target = jsonString["angolo_target"];

    if(avanti == 1){
      moveForward(ruota_sx, ruota_dx);
      delay(200);
      moveForward(0, 0);
      delay(500);
    }
    if(indietro == 1){      
      moveBack(ruota_sx, ruota_dx);
      moveForward(ruota_sx, ruota_dx);
      delay(200);
      moveForward(0, 0);
      delay(500);
    } 
  }

}



/***************************************************************************/
/*
Funzioni per la gestione delle ruote
*/
void rotateRobot(int direzione, float angolo_finale){
    /*
    direzione == 1 --> ruoto verso dx
    direzione == 0 --> ruoto verso sx
    */
    if(direzione==-1){
      return;
    }
    float angolo_attuale = getDegreeFromCompass();
    if(direzione == 1){
        while(1){
            angolo_attuale = getDegreeFromCompass();
            if(differenzaTraAngoli(angolo_attuale, angolo_finale)>5){
                Serial.print("Continuo a ruotare verso dx, ho una differenza di angoli pari a ");
                Serial.println(differenzaTraAngoli(angolo_attuale, angolo_finale));
                moveForward(130, 0); 
            } else {
                moveForward(0, 0);
                break;
            }
        }
    }
    if(direzione == 0){
        while(1){
            angolo_attuale = getDegreeFromCompass();
            if(differenzaTraAngoli(angolo_attuale, angolo_finale)>5){
                Serial.print("Continuo a ruotare verso sx, ho una differenza di angoli pari a ");
                Serial.println(differenzaTraAngoli(angolo_attuale, angolo_finale));
                moveForward(0, 130); 
            } else {
                moveForward(0, 0);
                break;
            }
        }
    }
}

float differenzaTraAngoli(float a, float b){
  return abs(a-b);
}

void moveBack(int speedLeftWheel, int speedRightWheel){
  analogWrite(E1, speedRightWheel);
  analogWrite(E2, speedLeftWheel);

  digitalWrite(I1, HIGH);
  digitalWrite(I2, LOW);
  digitalWrite(I3, LOW);
  digitalWrite(I4, HIGH);

}

void moveForward(int speedLeftWheel, int speedRightWheel){
  analogWrite(E1, speedRightWheel);
  analogWrite(E2, speedLeftWheel);

  digitalWrite(I1, LOW);
  digitalWrite(I2, HIGH);
  digitalWrite(I3, HIGH);
  digitalWrite(I4, LOW);

}

/***************************************************************************/
/*
Funzioni per la gestione della bussola
*/
void compassSetup(){
  Serial.println("Initialize HMC5883L");
  while (!compass.begin())
  {
    Serial.println("Could not find a valid HMC5883L sensor, check wiring!");
    delay(500);
  }

  // Set measurement range
  compass.setRange(HMC5883L_RANGE_1_3GA);

  // Set measurement mode
  compass.setMeasurementMode(HMC5883L_CONTINOUS);

  // Set data rate
  compass.setDataRate(HMC5883L_DATARATE_30HZ);

  // Set number of samples averaged
  compass.setSamples(HMC5883L_SAMPLES_8);

  // Set calibration offset. See HMC5883L_calibration.ino
  compass.setOffset(3, -39);
}

float getDegreeFromCompass(){
  Vector norm = compass.readNormalize();

  // Calculate heading
  float heading = atan2(norm.YAxis, norm.XAxis);

  // Set declination angle on your location and fix heading
  // You can find your declination on: http://magnetic-declination.com/
  // (+) Positive or (-) for negative
  // For Bytom / Poland declination angle is 4'26E (positive)
  // Formula: (deg + (min / 60.0)) / (180 / M_PI);
  float declinationAngle = (2.0 + (53.0 / 60.0)) / (180 / M_PI);
  heading += declinationAngle;

  // Correct for heading < 0deg and heading > 360deg
  if (heading < 0)
  {
    heading += 2 * PI;
  }

  if (heading > 2 * PI)
  {
    heading -= 2 * PI;
  }

  // Convert to degrees
  float headingDegrees = heading * 180/M_PI;

  // Output
  //   Serial.print(" Heading = ");
  //   Serial.print(heading);
  //   Serial.print(" Degress = ");
  //   Serial.print(headingDegrees);
  //   Serial.println();
    delay(100);
    return headingDegrees;
}
/***************************************************************************/
/*
Funzioni per la gestione della connessione al server
*/

void wifiSetup(){
  Serial.println("Wi-Fi setup iniziato");

  if(wifi.setOprToStation()){
    Serial.println("Ok per la stazione...");
  } else {
    Serial.println("Errore per la stazione...");
  }

  if (wifi.joinAP(SSID, PASSWORD)) {
        Serial.print("Collegato correttamente alla rete\r\n");
        Serial.print("IP: ");
        Serial.println(wifi.getLocalIP().c_str());
    } else {
        Serial.print("Errore nel collegamento alla rete\r\n");
    }

    if(wifi.disableMUX()){
      Serial.println("Single TCP connection ok");
    } else {
      Serial.println("Single TCP connection error");
    }

  Serial.println("Wi-Fi setup finito");
}

void createTCPConnection(){
  if(wifi.createTCP(SERVER_NAME, SERVER_PORT)){
    Serial.println("Create TCP connection ok");
  } else {
    Serial.println("Create TCP connection error");
  }
}

char* receivingDataTCP(){
  char data[256];
  uint8_t buffer[128] = {0};

  uint32_t len = wifi.recv(buffer, sizeof(buffer), 10000);
  if(len>0){
    for(uint32_t i=0; i<len; i++){
      data[i] = char(buffer[i]);
    }
  }
  return data;
}

void releaseTCPConnection(){
  if (wifi.releaseTCP()) {
        Serial.println("release tcp ok");
    } else {
        Serial.println("release tcp err");
    }
}


/***************************************************************************/
