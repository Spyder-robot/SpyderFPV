#include <Ultrasonic.h>
#include <SoftwareSerial.h>
#include <Wire.h>

SoftwareSerial softSerial(8, 9); // RX, TX

Ultrasonic ultrasonic(2, 3);

int adr = 0;

long bytes=0;
int ultradist=0;
boolean flag = false;

void setup()
{
  softSerial.begin(9600);
  Wire.begin(0x22);
  Wire.onRequest(sendData);
  Wire.onReceive(recvData);
  pinMode(5, OUTPUT);
  Serial.begin(115200);
  
  pinMode(13, OUTPUT);
  for (int i = 0; i < 3; i++)
  {
    digitalWrite(13, HIGH);
    delay(500);
    digitalWrite(13, LOW);
    delay(500);
  }
}


void loop()
{
  if (flag)
    digitalWrite(5, HIGH);
  else
    digitalWrite(5, LOW);

  while(Serial.available()>0)
  {
    Serial.read();
    bytes++;
  }
  ultradist = ultrasonic.read();
}


void recvData(int bts) 
{
  adr = Wire.read();
  while (Wire.available())
    Wire.read();
}


void sendData() 
{
  if (adr == 0x3b) //Ping
    Wire.write(222);

  if (adr == 1) //Ultrasonic
    Wire.write(ultradist&255);

  if (adr == 2) //Start LIDAR
  {
    Wire.write(1);
    flag = true;
  }
  if (adr == 3) //State LIDAR
  {
    Wire.write(bytes>>8);
    Wire.write(bytes&255);
  }
  if (adr == 4) //Stop LIDAR
  {
    Wire.write(1);
    flag = false;
  }
}
