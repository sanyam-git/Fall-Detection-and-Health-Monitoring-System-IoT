double alpha=0.75;
int period=20;
static double oldValue=0;
  
void setup(void){
  Serial.begin(9600);
  pinMode(A0,INPUT);
}

void loop(void){

  int beat=analogRead(A0);
  double value=alpha*oldValue+(1-alpha)*beat;
  
  Serial.print(" Heart Monitor "); 
  Serial.println(beat);
  oldValue=value;
  delay(period);  
}
