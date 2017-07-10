#include <Servo.h>
#include <NewPing.h>
#include "ESP8266.h"
#include <Wire.h>
#include <HMC5883L.h>
#include <ArduinoJson.h>


/*
Pin del sonar
*/
#define TRIGGER_PIN 50
#define ECHO_PIN 51
#define MAX_DISTANCE 200

/*
Pin degli infrarossi
*/
#define RIGHT_IR_PIN 22
#define BACK_IR_PIN 28
#define LEFT_IR_PIN 26
#define FRONT_IR_PIN 24

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
#define SSID        "Telecom-56943924"
#define PASSWORD    "lVGtZMVqI4XUQp5AWBcEHkQ7"

 // #define SSID        "VodafoneMobileWiFi-E3D656"
 // #define PASSWORD    "2926693643"

/*
Parametri del server
*/
#define SERVER_NAME "192.168.1.58"
#define SERVER_PORT (1931)

Servo myservo;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
ESP8266 wifi(Serial1, 115200);
HMC5883L compass;


// infrarossi
int IRLeftVal;
int IRFrontVal;
int IRRightVal;
int IRBackVal;
// sonar
int sonar_value_front;
int sonar_value_right;
int sonar_value_left;
// compass
float compass_value;

// Questa variabile mi serve per capire se sono in una fase iniziale o meno
int robot_init;

// Variabile usata per i pacchetti JSON che il robot manda al server
StaticJsonBuffer<200> jsonBuffer;
String datiSensoriali = "{\"sonar_centro\":-1, \"sonar_sinistra\": -1, \"sonar_destra\": -1, \"IR_destra\": -1, \"IR_sinistra\": -1, \"IR_centro\": -1, \"IR_dietro\": -1, \"bussola\": -1}";
JsonObject& root = jsonBuffer.parseObject(datiSensoriali);

void setup(){

  myservo.attach(6);
  myservo.write(90);

  pinMode(FRONT_IR_PIN, INPUT);
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

  robot_init = 0;
}


void loop(){
  
  createTCPConnection();
  
  // Mando i dati sensoriali al server
  sendSensorDataToServer();
  
  // Ricevo la risposta dal server
  char* comandoDaServer = receivingDataTCP();
  analizzaDati(comandoDaServer);
  
  releaseTCPConnection();
  delay(2000);
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
  Serial.println("Dati inviati");
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
  Serial.println(azione);
  
  if(strcmp(azione, "movimento") == 0) {
    char* move = jsonString["direzione"];
    if(strcmp(move, "davanti") == 0) {
      Serial.println("Mi muovo verso avanti");
      moveForward(225, 250);
      delay(500);
      moveForward(0, 0);
    }
    if(strcmp(move, "destra") == 0) {
      Serial.println("Mi muovo verso destra");
      rotateRobot(1, 60); //ruoto verso dx
      moveForward(225, 250); 
      delay(1500);
      moveForward(0, 0);
      delay(1000);
    }
    if(strcmp(move, "sinistra") == 0) {
      Serial.println("Mi muovo verso sinistra");
      rotateRobot(0, -60); //ruoto verso sx
      moveForward(225, 250);
      delay(1500);
      moveForward(0, 0);
      delay(1000);
    }
  }
}


/***************************************************************************/
/*
Funzioni per la gestione dei sensori
*/
void getSensorsData(){
  Serial.println("\nACQUISIZIONE DATI");
  Serial.println("\nAcquisisco i dati davanti");
  sonar_value_front = sonar.ping_cm();
  delay(1000);

  Serial.println("Acquisisco i dati a sinistra");
  myservo.write(0);
  delay(500);
  sonar_value_left = sonar.ping_cm();
  delay(1000);

  Serial.println("Acquisisco i dati a destra");
  myservo.write(180);
  delay(500);
  sonar_value_right = sonar.ping_cm();
  delay(1000);
  myservo.write(90);

  IRLeftVal = digitalRead(LEFT_IR_PIN);
  IRFrontVal = digitalRead(FRONT_IR_PIN);
  IRRightVal = digitalRead(RIGHT_IR_PIN);
  IRBackVal = digitalRead(BACK_IR_PIN);
  
  compass_value = getDegreeFromCompass();

  root["azione"] = "percezione";
  root["sonar_centro"] = sonar_value_front;
  root["sonar_destra"] = sonar_value_right;
  root["sonar_sinistra"] = sonar_value_left;
  root["IR_destra"] = IRRightVal;
  root["IR_centro"] = IRFrontVal;
  root["IR_dietro"] = IRBackVal;
  root["IR_sinistra"] = IRLeftVal;
  root["bussola"] = compass_value;
  Serial.println("Ho preso i dati sensoriali");
}

void printSensorsData(){
  Serial.println("\nStampo i dati dei sensori");

  Serial.println("Sonar");
  Serial.print("Destra: ");
  Serial.print(sonar_value_right);
  Serial.print("\tSinistra: ");
  Serial.print(sonar_value_left);
  Serial.print("\tDavanti: ");
  Serial.print(sonar_value_front);

  Serial.println("\nInfrarossi");
  Serial.print("Destra: ");
  Serial.print(IRRightVal);
  Serial.print("\tSinistra: ");
  Serial.print(IRLeftVal);
  Serial.print("\tDavanti: ");
  Serial.print(IRFrontVal);
  Serial.print("\tDietro: ");
  Serial.print(IRBackVal);

}

/***************************************************************************/
/*
Funzioni per la gestione delle ruote
*/
// dir puo' essere: 1 per dx, 0 per sx
void rotateRobot(int dir, int angle){
  
  float startD = getDegreeFromCompass();
  float finalD = startD + angle;
  
  if(finalD >= 360){
    finalD = finalD - 359;
  }
  if(finalD<=0){
    finalD = finalD + 359;
  }
  Serial.print("Posizione iniziale angolare: ");
  Serial.println(startD);
  Serial.print("Rotazione desiderata: ");
  Serial.println(angle);
  Serial.print("Posizione finale angolare: ");
  Serial.println(finalD);
  //rotazione verso dx
  if(dir == 1) {
    while(true) {
      startD=getDegreeFromCompass();
      Serial.print("Ruoto il robot verso dx, mancano: ");
      Serial.println(error(startD, finalD));
      if(error(startD, finalD)<5){
        moveForward(0, 0);
        Serial.println("Raggiunta posizione che cercavo verso dx");
        break;
      } else {
        moveForward(250, 0);
        delay(30);
        moveBack(0, 250);
        delay(30);
        moveForward(0, 0);
        delay(100);
      }
    }
  }
  if(dir == 0) {
    while(true) {
      startD = getDegreeFromCompass();
      Serial.print("Ruoto il robot verso sx, mancano: ");
      Serial.println(error(startD, finalD));
      if(error(startD, finalD)<5){
        moveForward(0, 0);
        Serial.println("Raggiunta posizione che cercavo verso sx");
        break;
      } else {
        moveForward(0, 250);
        delay(30);
        moveBack(250,0);
        delay(30);
        moveForward(0, 0);
        delay(100);
      }
    }
  }
  
  
}

float error(float a, float b){
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
