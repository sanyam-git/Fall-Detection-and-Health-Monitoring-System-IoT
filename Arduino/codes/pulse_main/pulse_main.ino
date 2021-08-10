#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Ashish_2.4";
const char* password = "tindabhindi";
const char* mqtt_server = "192.168.0.199";// Your Raspberry Pi IP address

#define samp_siz 6
#define rise_threshold 8
float reads[samp_siz], sum;
float last, reader, Start, Now;
float first, Second, third, fourth, before, print_value;
float s_pulse;
bool rising;
int rise_count;
int n, k, ptr;
long int last_beat;

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[50];
int value = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  digitalWrite(BUILTIN_LED, HIGH);
  Serial.begin(115200);

  setup_wifi();
  hrinit();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String message = "";  // Incoming message
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
    message+=(char)payload[i];
  }
  Serial.println();

  // Switch on the LED if an 1 was received as first character
  /*if(String(topic)=="from_rpi") {

  }*/

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("to_rpi", "hello world");
      // ... and resubscribe
      client.subscribe("from_rpi");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void hrinit(){
    for (int i = 0; i < samp_siz; i++)
      reads[i] = 0;
    sum = 0;
    ptr = 0;
  }
  
float pulse ()
{
  unsigned long _now = millis();
  unsigned long _last = millis();
  float pulse;
  s_pulse=0;
  k=0;
  do{
      // calculate an average of the sensor
      // during a 20 ms period (this will eliminate
      // the 50 Hz noise caused by electric light
      n = 0;
      Start = millis();
      reader = 0;
      do
      {
        reader += analogRead (A0);
        n++;
        Now = millis();
      }
      while (Now < Start + 20); 
      reader /= n;  // we got an average
      
      // Add the newest measurement to an array
      // and subtract the oldest measurement from the array
      // to maintain a sum of last measurements
      sum -= reads[ptr];
      sum += reader;
      reads[ptr] = reader;
      last = sum / samp_siz;
      //Serial.print("Heart monitor ");
      //Serial.println(last);
      if (last > before && last > 75)
      {
        rise_count++;
        if (!rising && rise_count > rise_threshold)
        {
          // Ok, we have detected a rising curve, which implies a heartbeat.
          // Record the time since last beat, keep track of the two previous
          // times (first, second, third) to get a weighed average.
          // The rising flag prevents us from detecting the same rise more than once.
          rising = true;
          first = millis() - last_beat;
          last_beat = millis();

          // Calculate the weighed average of heartbeat rate
          // according to the three last beats
          print_value = 60000 / (0.4 * first + 0.3 * Second + 0.3 * third);
          s_pulse += print_value;
          k+=1;
          //Serial.print(print_value);
          //Serial.print('\n');
          fourth = third;
          third = Second;
          Second = first;    
        }
      }
      else
      {
        // Ok, the curve is falling
        rising = false;
        rise_count = 0;
      }
      before = last;
      ptr++;
      ptr %= samp_siz;
      _now = millis();
  }while(_now - _last < 1600);
  if(k == 0){
    if(last<75)
      pulse=-1;
    else
      pulse =0;
  }
  else
    pulse = (s_pulse/k);
  return pulse;
}

void loop() {
  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  delay(50);
  
  unsigned long now_ = millis();
  float rate = pulse();
  if (now_ - lastMsg > 3000) {
    lastMsg = millis();
    Serial.print("pulse ");
    Serial.println(rate);
    snprintf (msg, MSG_BUFFER_SIZE, "%f", rate);
    client.connect("ESP8266Client1");
    client.publish("pulse",msg);
  }
}
