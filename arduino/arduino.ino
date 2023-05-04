#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN 2 //temp & hum
#define DHTTYPE DHT11

#define trigPin 7
#define echoPin 6

DHT dht(DHTPIN, DHTTYPE);

int irPin = 3; // zavadzas

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
    // Send ultrasonic pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read infrared sensor
  int irValue = digitalRead(irPin);

  // Read sensor values
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.034 / 2;

  // Create a JSON object and populate it with sensor readings
  StaticJsonDocument<200> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["distance"] = distance;
  doc["ir"] = irValue;

  // Serialize the JSON object to a string
  String jsonString;
  serializeJson(doc, jsonString);

  // Send the JSON string over the Serial port
  Serial.println(jsonString);

  delay(1000);

}
