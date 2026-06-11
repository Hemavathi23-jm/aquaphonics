#include <WiFi.h>
#include <WebServer.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ---------------- WIFI ----------------
const char* ssid = "OPPOA53";
const char* password = "Abhi1234";

WebServer server(80);

// ---------------- SENSOR PINS ----------------
#define ONE_WIRE_BUS 2
#define PH_PIN 34
#define MOISTURE_PIN 35

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

// ---------------- VARIABLES ----------------
float temperature = 0;
float phValue = 0;
int moistureValue = 0;

// ---------------- READ SENSORS ----------------
void readSensors() {

  // Temperature
  tempSensor.requestTemperatures();
  temperature = tempSensor.getTempCByIndex(0);

  // pH Average Reading
  long phSum = 0;
  for (int i = 0; i < 10; i++) {
    phSum += analogRead(PH_PIN);
    delay(10);
  }

  float phRaw = phSum / 10.0;
  float phVoltage = phRaw * (3.3 / 4095.0);

  // Calibration
  phValue = 7 + ((1.10 - phVoltage) / 0.18);

  // Moisture
  moistureValue = analogRead(MOISTURE_PIN);
}

// ---------------- HANDLE WEB REQUEST ----------------
void handleData() {

  readSensors();

  String json = "{";
  json += "\"temperature\":" + String(temperature, 2) + ",";
  json += "\"ph\":" + String(phValue, 2) + ",";
  json += "\"moisture\":" + String(moistureValue);
  json += "}";

  server.send(200, "application/json", json);
}

// ---------------- SETUP ----------------
void setup() {

  Serial.begin(115200);
  delay(2000);

  Serial.println("\n\n--- Aquaponics System Starting ---");

  pinMode(ONE_WIRE_BUS, INPUT_PULLUP);
  tempSensor.begin();

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected ✔");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/data", handleData);
  server.begin();

  Serial.println("Web Server Started ✔");
}

// ---------------- LOOP ----------------
void loop() {

  server.handleClient();  // Required for web server

  readSensors();

  Serial.println("------ Live Sensor Data ------");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("pH: ");
  Serial.println(phValue);

  Serial.print("Moisture: ");
  Serial.println(moistureValue);

  Serial.println("-------------------------------\n");

  delay(2000);
}