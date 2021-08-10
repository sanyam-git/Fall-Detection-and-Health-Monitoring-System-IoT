#include <DHT.h>
#define DHT11_PIN 2
DHT DHT(DHT11_PIN,DHT11);

void setup()
{
Serial.begin(115200);
DHT.begin();
}
void loop()
{
float tempC = DHT.readTemperature();
float tempF = DHT.convertCtoF(tempC);
float humidity = DHT.readHumidity();

Serial.print("Temperature (C) = ");
Serial.println(tempC);
Serial.print("Temperature (F) = ");
Serial.println(tempF);
Serial.print("Humidity = ");
Serial.println(humidity);
delay(3000);
}
