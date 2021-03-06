#include <Servo.h>
#include "ESP8266.h"
#include <Wire.h>
#include <HMC5883L.h>
#include <ArduinoJson.h>

/*
Pin Motori
*/
#define ENA 8
#define ENB 13
#define IN1 9
#define IN2 10
#define IN3 11
#define IN4 12

/*
Pin degli infrarossi
*/

#define RIGHT_IR_PIN 30
#define TOP_IR_PIN 32
#define LEFT_IR_PIN 22
#define FRONT_IR_PIN 26
#define FRONT_IR_RIGHT 28
#define FRONT_IR_LEFT 24
#define BARRA_DX_PIN 34 
#define BARRA_SX_PIN 36
#define BARRA_CENTRO_PIN 38
/*
Costanti per la connessione con il server
*/
//#define SSID        "Telecom-56943924"
//#define PASSWORD    "lVGtZMVqI4XUQp5AWBcEHkQ7"

//#define SSID        "VodafoneMobileWiFi-E3D656"
//#define PASSWORD    "2926693643"

#define SSID        "TIM-18898433"
#define PASSWORD    "**TeleImap3**"

//#define SSID "ASUS"
//#define PASSWORD "robomiller"
/*
Parametri del server
*/
#define SERVER_NAME "192.168.1.132"
#define SERVER_PORT (1931)

/*
Costruttori per gli oggetti
*/
Servo myservo;
Servo myservo2;
ESP8266 wifi(Serial1, 115200);
HMC5883L compass;

// timer
unsigned long t0 = 0;

// infrarossi
int IRLeftVal;
int IRFrontVal;
int IRRightVal;
int IRTopVal;
int IRFrontDxVal;
int IRFrontSxVal;
int IRBarraSxVal;
int IRBarraDxVal;
int IRBarraFrontVal;

// compass
float compass_value;

// Variabile usata per i pacchetti JSON che il robot manda al server
StaticJsonBuffer<256> jsonBuffer;
String datiSensoriali = "{\"ID\": \"Arduino\", \"IR_dx\": -1, \"IR_sx\": -1, \"IR_cdx\": -1, \"IR_c\": -1, \"IR_csx\": -1, \"IR_t\": -1, \"buss\": -1, \"vengoDa\": 1}";
JsonObject& root = jsonBuffer.parseObject(datiSensoriali);

// Variabile sterzatura; in base a dove mi dirigo, allora tratto l'ostacolo davanti in due modi differenti:
//  - 0 per sx
//  - 1 per dx
int sterzatura = 0;

void setup(){
  
  myservo.attach(6);
  myservo2.attach(5);
  myservo.write(0);
  myservo2.write(180);
  delay(400);
  pinMode(FRONT_IR_PIN, INPUT);
  pinMode(FRONT_IR_RIGHT, INPUT);
  pinMode(FRONT_IR_LEFT, INPUT);
  pinMode(TOP_IR_PIN, INPUT);
  pinMode(LEFT_IR_PIN, INPUT);
  pinMode(RIGHT_IR_PIN, INPUT);
  pinMode(BARRA_DX_PIN, INPUT);
  pinMode(BARRA_SX_PIN, INPUT);
  pinMode(BARRA_CENTRO_PIN, INPUT);

  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.begin(115200);
  
  wifiSetup();
  compassSetup();
  
  
  fermati();
}

void loop(){
  createTCPConnection();
  // Mando i dati sensoriali al server
  sendSensorDataToServer();
  // Ricevo la risposta dal server
  char* comandoDaServer = receivingDataTCP();
  analizzaComando(comandoDaServer);
  releaseTCPConnection();
}

/***************************************************************************/
/*
Funzione per mandare i dati al server
*/
void sendSensorDataToServer(){
  getSensorsData();
  char dati_sensoriali[170];
  root.printTo(dati_sensoriali, sizeof(dati_sensoriali));
  wifi.send(dati_sensoriali, strlen(dati_sensoriali));
}
  
void getSensorsData(){
  
  IRLeftVal = digitalRead(LEFT_IR_PIN);
  IRFrontVal = digitalRead(FRONT_IR_PIN);
  IRRightVal = digitalRead(RIGHT_IR_PIN);
  IRTopVal = digitalRead(TOP_IR_PIN);
  IRFrontDxVal = digitalRead(FRONT_IR_RIGHT);
  IRFrontSxVal = digitalRead(FRONT_IR_LEFT);
  IRBarraSxVal = digitalRead(BARRA_SX_PIN);
  IRBarraDxVal = digitalRead(BARRA_DX_PIN);
  IRBarraFrontVal = digitalRead(BARRA_CENTRO_PIN);
  
  compass_value = getDegreeFromCompass();

  root["IR_dx"] = IRRightVal;
  root["IR_c"] = IRFrontVal;
  root["IR_t"] = IRTopVal;
  root["IR_sx"] = IRLeftVal;
  root["IR_cdx"] = IRFrontDxVal;
  root["IR_csx"] = IRFrontSxVal;
  root["IR_b"] = IRBarraFrontVal;
  root["IR_bsx"] = IRBarraSxVal;
  root["IR_bdx"] = IRBarraDxVal;
  root["buss"] = compass_value;
  //root.printTo(Serial);
}

void analizzaComando(char* comandi){
    /*
    I possibili comandi per il robot sono:
    - comando == 0 --> init
    - comando == 1 --> movimento
    - comando == 2 --> avvicinamento
    - comando == 3 --> prendi/rilascia oggetto (per scopi di testing)
    */
    StaticJsonBuffer<128> jsonStringBuffer;
    JsonObject& jsonString = jsonStringBuffer.parseObject(comandi);

    if(!jsonString.success()) {
        Serial.println("parseObject() failed");
        return;
    }
    
    int comando = jsonString["comando"];
    int con_oggetto = jsonString["con_oggetto"];
    sterzatura = jsonString["sterzatura_preferita"];
    
    if(comando == 0){
        float angolo_target = jsonString["angolo_target"];
        int verso_rotazione = jsonString["verso_rotazione"];
        rotateRobot(verso_rotazione, angolo_target, con_oggetto);
        return;
    }

    int velocitaRuotaSx = jsonString["ruota_sx"];
    int velocitaRuotaDx = jsonString["ruota_dx"];
    
    if(comando == 1){
        //Il robot si puo' muovere liberamente, deve solamente evitare gli ostacoli in modo reattivo
        prendiDecisione(velocitaRuotaSx, velocitaRuotaDx, con_oggetto);
    }

    if(comando == 2){
      float angolo_target = jsonString["angolo_target"];
      int verso_rotazione = jsonString["verso_rotazione"];
      avvicinati(verso_rotazione, angolo_target, velocitaRuotaSx, velocitaRuotaDx, con_oggetto);
      
    }

    if(comando == 3) {
      prendiOggetto(con_oggetto);
    }

}

/***************************************************************************/
/*
Funzioni per la gestione delle ruote
*/
void rotateRobot(int verso_rotazione, float angolo_finale, int con_oggetto){
    /*
    verso_rotazione == 1 --> ruoto verso dx
    verso_rotazione == 0 --> ruoto verso sx
    */
    int vengoDa = root["vengoDa"];
    
    int velocitaRuotaSx = 160;
    int velocitaRuotaDx = 160;
    if(con_oggetto == 1){
      velocitaRuotaSx = 230;
      velocitaRuotaDx = 230;
    }
    if(verso_rotazione==-1){
      return;
    }

    float angolo_attuale = getDegreeFromCompass();
    if(verso_rotazione == 1){
        while(1){
            angolo_attuale = getDegreeFromCompass();
            if(differenzaTraAngoli(angolo_attuale, angolo_finale)>5){
                muoviAvanti(velocitaRuotaSx, 0);
                t0 = millis();
                while (millis() - t0 < 200){
                  getSensorsData();
                  if(con_oggetto == 1){
                    IRTopVal = IRBarraFrontVal;
                    IRFrontDxVal = IRBarraDxVal;
                    IRFrontSxVal = IRBarraSxVal;

                   if (IRLeftVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                   }

                 }
                 if (con_oggetto == 0) {
                  if (IRLeftVal == 0 || IRFrontVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                 }
                 }
                }
                fermati();   
            } else {
                fermati();
                break;
            }
        }
    }
    if(verso_rotazione == 0){
        while(1){
            angolo_attuale = getDegreeFromCompass();
            if(differenzaTraAngoli(angolo_attuale, angolo_finale)>5){
                muoviAvanti(0, velocitaRuotaDx);
                t0 = millis();
                while (millis() - t0 < 200){
                  getSensorsData();
                  if(con_oggetto == 1){
                    IRTopVal = IRBarraFrontVal;
                    IRFrontDxVal = IRBarraDxVal;
                    IRFrontSxVal = IRBarraSxVal;

                   if (IRLeftVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                   }

                 }
                 if (con_oggetto == 0) {
                  if (IRLeftVal == 0 || IRFrontVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                 }
                 }
                }
                fermati();
            } else {
                fermati();
                break;
            }
        }
    }
}

float differenzaTraAngoli(float a, float b){
  return abs(a-b);
}

void fermati(){
    analogWrite(ENA,0); // blocca il motore A 
    analogWrite(ENB,0); // blocca il motore B 
}

void muoviAvanti(int velocitaRuotaSx, int velocitaRuotaDx){
    
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, velocitaRuotaDx);
    analogWrite(ENB, velocitaRuotaSx);
    
}

void muoviIndietro(int velocitaRuotaSx, int velocitaRuotaDx){
    
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, velocitaRuotaDx);
    analogWrite(ENB, velocitaRuotaSx);
}

/*
Funzioni che si occupano della parte reattiva del robot in base agli ostacoli che determina
*/
void prendiDecisione(int velocitaRuotaSx, int velocitaRuotaDx, int con_oggetto){
    
    getSensorsData();
    
    if(con_oggetto == 1){
      IRTopVal = IRBarraFrontVal;
      IRFrontDxVal = IRBarraDxVal;
      IRFrontSxVal = IRBarraSxVal;
      
    } 

    if(IRTopVal == 1 && IRFrontDxVal == 1 && IRFrontSxVal == 1 && IRLeftVal == 1 && IRRightVal == 1){
        muoviAvanti(velocitaRuotaSx, velocitaRuotaDx);
        root["vengoDa"] = 1;
        t0 = millis();
                while (millis() - t0 < 300){
                  getSensorsData();
                  if(con_oggetto == 1){
                    IRTopVal = IRBarraFrontVal;
                    IRFrontDxVal = IRBarraDxVal;
                    IRFrontSxVal = IRBarraSxVal;

                   if (IRLeftVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                 }
                  } 
                  if (IRLeftVal == 0 || IRFrontVal == 0 || IRRightVal == 0 || IRTopVal == 0 || IRFrontDxVal == 0 || IRFrontSxVal == 0){
                    root["vengoDa"] = 0;
                    fermati();
                    return;
                 }
                }
        fermati();
        return;
    }

    if(IRTopVal == 0 and (IRFrontDxVal == 0 || IRRightVal == 0)){
      
        muoviIndietro(180, 0);
        t0 = millis();
        while (millis() - t0 < 200);
        root["vengoDa"] = 0;
        fermati();
        return;
    }

    if(IRTopVal == 0 and (IRFrontSxVal == 0 || IRLeftVal == 0)){
        muoviIndietro(0, 180);
        t0 = millis();
        while (millis() - t0 < 200);
        root["vengoDa"] = 0;
        fermati();
        return;
    }

    if(IRFrontSxVal == 0 || IRLeftVal == 0){
        muoviIndietro(0, 180);
        t0 = millis();
        while (millis() - t0 < 200);
        //delay(200);
        root["vengoDa"] = 0;
        fermati();
        return;
    }

    if(IRFrontDxVal == 0 || IRRightVal == 0){
        muoviIndietro(180, 0);
        t0 = millis();
        while (millis() - t0 < 200);
        //delay(200);
        root["vengoDa"] = 0;
        fermati();
        return;
    }

    if(IRTopVal == 0){
        if(sterzatura == 0){
           muoviIndietro(180, 0);
        } else {
          muoviIndietro(0, 180);
        }
        t0 = millis();
        while (millis() - t0 < 200);
        root["vengoDa"] = 0;
        fermati();
        return;
    }
}

void avvicinati(int verso_rotazione, int angolo_target, int velocitaRuotaSx, int velocitaRuotaDx, int con_oggetto){
    
    rotateRobot(verso_rotazione, angolo_target, con_oggetto);
    muoviAvanti(velocitaRuotaSx, velocitaRuotaDx);
    t0 = millis();
    while (millis() - t0 < 300);
    fermati();
}

void prendiOggetto(int con_oggetto){
  if(con_oggetto==0){
    while(IRFrontVal == 1){
      getSensorsData();
      if(IRFrontDxVal == 0){
        muoviIndietro(0, 150);
        t0 = millis();
        while (millis() - t0 < 100);
        fermati();
      }
      if(IRFrontSxVal == 0){
        muoviIndietro(150, 0);
        t0 = millis();
        while (millis() - t0 < 100);
        fermati();
      }
      if(IRFrontVal == 0){
        for(int i=5; i<100; i+=5){
          myservo.write(i);
          myservo2.write(180 - i);
          t0 = millis();
          while (millis() - t0 < 100);
         }
          muoviIndietro(250, 250);
          t0 = millis();
          while (millis() - t0 < 800);
          fermati();
          return;
      } else {
        muoviAvanti(160, 160);
        t0 = millis();
        while (millis() - t0 < 200);
        fermati();
      }
    }
    
  }

  if(con_oggetto == 1){
    while(IRBarraFrontVal == 1){
      getSensorsData();
      if(IRBarraFrontVal == 0) {
        for(int i=100; i>0; i-=5){
          myservo.write(i);
          myservo2.write(85 - i);
          t0 = millis();
          while (millis() - t0 < 100);
        }
        muoviIndietro(250, 250);
          t0 = millis();
          while (millis() - t0 < 800);
          fermati();
      } else {
        muoviAvanti(190, 190);
        t0 = millis();
        while (millis() - t0 < 200);
        fermati();
      }
    }
    return;
  }
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

