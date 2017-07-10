#include <ArduinoJson.h>
#include "ESP8266.h"
#include <NewPing.h>

//#define SSID        "Telecom-56943924"
//#define PASSWORD    "lVGtZMVqI4XUQp5AWBcEHkQ7"

 #define SSID        "VodafoneMobileWiFi-E3D656"
 #define PASSWORD    "2926693643"

#define SERVER_NAME "192.168.0.101"
#define SERVER_PORT (1931)

#define TRIGGER_PIN 50
#define ECHO_PIN 51
#define MAX_DISTANCE 200
#define IRPinRight 22
#define IRPinCenter 24
#define IRPinLeft 26

#define E1 8
#define E2 13
#define I1 9
#define I2 10
#define I3 11
#define I4 12

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
ESP8266 wifi(Serial1, 115200);

// infrarossi
int IRLeftVal;
int IRCenterVal;
int IRRightVal;
// sonar
int sonar_value;

StaticJsonBuffer<200> jsonBuffer;
String input = "{\"id\":\"Arduino\", \"sonar\":-1, \"IRLeft\": -1, \"IRCenter\": -1, \"IRRight\": -1}";
JsonObject& root = jsonBuffer.parseObject(input);

void setup() {
  pinMode(IRPinLeft, INPUT);
  pinMode(IRPinCenter, INPUT);
  pinMode(IRPinRight, INPUT);

  pinMode(E1, OUTPUT);
  pinMode(E2, OUTPUT);
  pinMode(I1, OUTPUT);
  pinMode(I2, OUTPUT);
  pinMode(I3, OUTPUT);
  pinMode(I4, OUTPUT);

  Serial.begin(115200);
  wifi_setup();
}

void loop() {

  create_TCP_connection();

  // sending data to server
  get_sensors_data();
  char message[256];
  root.printTo(message, sizeof(message));
  wifi.send(message, strlen(message));

  // receiving data from server
  char* data = receiving_data_TCP();

  // moving the robot depending on the received commands from server
  move(data);
  release_TCP_connection();

  delay(100);
}

void wifi_setup(){
  Serial.println("Wi-Fi setup begins");

  if(wifi.setOprToStation()){
    Serial.println("To station ok...");
  } else {
    Serial.println("To station error...");
  }

  if (wifi.joinAP(SSID, PASSWORD)) {
        Serial.print("Join AP success\r\n");
        Serial.print("IP: ");
        Serial.println(wifi.getLocalIP().c_str());
    } else {
        Serial.print("Join AP failure\r\n");
    }

    if(wifi.disableMUX()){
      Serial.println("Single TCP connection ok");
    } else {
      Serial.println("Single TCP connection error");
    }

  Serial.println("Wi-Fi setup ends");
}

void create_TCP_connection(){
  if(wifi.createTCP(SERVER_NAME, SERVER_PORT)){
    Serial.println("Create TCP connection ok");
  } else {
    Serial.println("Create TCP connection error");
  }
}

void release_TCP_connection(){
  if (wifi.releaseTCP()) {
        Serial.println("release tcp ok");
    } else {
        Serial.println("release tcp err");
    }
}

void get_sensors_data(){

  sonar_value = sonar.ping_cm();
  IRLeftVal = digitalRead(IRPinLeft);
  IRCenterVal = digitalRead(IRPinCenter);
  IRRightVal = digitalRead(IRPinRight);

  root["sonar"] = sonar_value;
  root["IRLeft"] = IRLeftVal;
  root["IRCenter"] = IRCenterVal;
  root["IRRight"] = IRRightVal;

}

char* receiving_data_TCP(){
  char data[256];
  uint8_t buffer[128] = {0};

  uint32_t len = wifi.recv(buffer, sizeof(buffer), 10000);
  if(len>0){
    for(uint32_t i=0; i<len; i++){
      data[i] = char(buffer[i]);
    }
  }
  Serial.println("New data received");
  Serial.println(data);
  return data;
}

void move(char* data){

  StaticJsonBuffer<256> jsonStringBuffer;
  JsonObject& jsonString = jsonStringBuffer.parseObject(data);

  int forward = jsonString["forward"];
  int back = jsonString["back"];
  int speedLeftWheel = jsonString["speedLeftWheel"];
  int speedRightWheel = jsonString["speedRightWheel"];

  if(forward == 1) {
    move_forward(speedLeftWheel, speedRightWheel);
  }
  if(back == 1) {
    move_back(speedLeftWheel, speedRightWheel);
  }
  if (forward == 1 && back == 1){
    take_decision();
  }

}

void move_forward(int speedLeftWheel, int speedRightWheel){
  analogWrite(E1, speedRightWheel);
  analogWrite(E2, speedLeftWheel);

  digitalWrite(I1, HIGH);
  digitalWrite(I2, LOW);
  digitalWrite(I3, LOW);
  digitalWrite(I4, HIGH);

}

void move_back(int speedLeftWheel, int speedRightWheel){
  analogWrite(E1, speedRightWheel);
  analogWrite(E2, speedLeftWheel);

  digitalWrite(I1, LOW);
  digitalWrite(I2, HIGH);
  digitalWrite(I3, HIGH);
  digitalWrite(I4, LOW);

}

void take_decision(){
  move_back(150, 0); // vado indietro e calcolo la distanza verso sx con il sonar
  int sonar_value_left = sonar.ping_cm(); //prendo il valore del sonar a sx
  delay(200);
  move_forward(150, 0); // mi rimetto in posizione iniziale;
  delay(200);
  move_back(0, 150); // vado indietro per calcolare la distanza verso dx con il sonar;
  int sonar_value_right = sonar.ping_cm();
  delay(200);
  if(sonar_value_left <= sonar_value_right){
    move_back(150, 0); // mi giro verso sx
  } else { 
    move_back(0, 150); // mi giro verso dx 
  }
  delay(200);
}

