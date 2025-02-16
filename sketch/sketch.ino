#include <WiFi.h>
#include <HTTPClient.h>

// Replace these with your WiFi credentials
const char* ssid = "MIWIFI_E444";
const char* password = "246J9F4K";

// Replace with your backend server's IP address and port
const char* serverUrl = "http://192.168.1.134:5000/api/audio";

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting ESP32 Fake Microphone Project");

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi.");

  // Initialize random number generator
  randomSeed(analogRead(0));
}

void loop() {
  // Simulate a microphone reading by generating a random number (0 - 1023)
  int simulatedMicValue = random(0, 1024);
  String payload = "{\"micValue\": " + String(simulatedMicValue) + "}";
  
  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);
    if(httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.print("Error in POST: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected.");
  }
  
  // Wait 5 seconds before sending the next simulated reading
  delay(5000);
}
