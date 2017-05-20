#include <ArduinoJson.h>
#include "ESP8266.h"
#include <NewPing.h>


#define SSID        "Telecom-56943924"
#define PASSWORD    "lVGtZMVqI4XUQp5AWBcEHkQ7"

#define SERVER_NAME "192.168.1.11"
#define SERVER_PORT (1931)

#define TRIGGER_PIN 50
#define ECHO_PIN 51
#define MAX_DISTANCE 200
#define IRPin 24

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
ESP8266 wifi(Serial1, 115200);
int IRVal;
int sonar_value;

StaticJsonBuffer<200> jsonBuffer;
String input = "{\"id\":\"Arduino\", \"sonar\":-1, \"IR\": -1}";
JsonObject& root = jsonBuffer.parseObject(input);

void setup() {
  pinMode(IRPin, INPUT);
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


  move(data);
  release_TCP_connection();

  delay(5000);
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
  IRVal = digitalRead(IRPin);
  root["sonar"] = sonar_value;
  root["IR"] = IRVal;

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
  Serial.println(data);
  return data;
}

void move(char* data){
  StaticJsonBuffer<256> jsonStringBuffer;
  JsonObject& jsonString = jsonStringBuffer.parseObject(data);
  int forward = jsonString["forward"];
  int back = jsonString["back"];
  int right = jsonString["right"];
  int left = jsonString["left"];
  int rotate = jsonString["rotate"];

  if(forward == 1 && right == 0){
    Serial.println("Muoviti verso nord");
  } else {
    Serial.println("Mettiti a cono rovesciato");
  }
}
