// Soft Serial
#include <AltSoftSerial.h>
AltSoftSerial softSerial;

#define LED_PIN 6
#define U_PIN A2
#define I_PIN A3
#define FAN_PIN 3

long senstimer;
long sendtimer;
long temptimer;

// Temperature
#include <OneWire.h>
#include <DallasTemperature.h>
OneWire oneWire(10);
DallasTemperature sensors(&oneWire);
DeviceAddress temp1, temp0;
float t0 = 0, t1 = 0, vol = 0, cur = 0;
int sens[20][5];

// I2C
#include <Wire.h>
int adr = 0;

// NeoPixel
#include <Adafruit_NeoPixel.h>
Adafruit_NeoPixel neostrip(32, 5, NEO_GRB + NEO_KHZ800);

// Servo
#include <DynamixelSerial.h>
int id = 254;
int st = 0;

boolean led = false;
boolean fan = false;
boolean test = false;
boolean ledstate = false;
boolean fanstate = false;

void setup() 
{
  int i;

  pinMode(LED_PIN, OUTPUT);
  for (i = 0; i < 3; i++)
  {
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
  }
  analogWrite(LED_PIN, 1);

  senstimer = millis();
  sendtimer = millis();

  // Soft Serial
  softSerial.begin(9600);

  // I2C
  Wire.begin(0x11);
  Wire.onRequest(sendData);
  Wire.onReceive(recvData);

  // NeoPixel
  neostrip.begin();

  // Temperature
  sensors.begin();
  sensors.getAddress(temp0, 0);
  sensors.getAddress(temp1, 1);
  gettemp();

  // Servo
  Dynamixel.setSerial(&Serial);
  Dynamixel.begin(1000000, 2);
}


void loop() 
{
    
  if (sendtimer + 1000 < millis())
  {
    softSerial.println("<V=" + String(vol) + ">");
    softSerial.println("<I=" + String(cur) + ">");
    softSerial.println("<T1=" + String(t0) + ">");
    softSerial.println("<T2=" + String(t1) + ">");
    sendtimer = millis();
  }

  if (senstimer + 50 < millis())
  {
    getsens();
    senstimer = millis();
  }

  if (temptimer + 10000 < millis())
  {
    gettemp();
    temptimer = millis();
  }

  if (led)
  {
    ledf();
    led = false;
  }

  if (fan)
  {
    fanf();
    fan = false;
  }

  if (test)
  {
    testf();
    test = false;
  }
   
  st=0;
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
    Wire.write(111);

  if (adr == 1) //Current state
    Wire.write(st);

  if (adr > 1)
  {
    st = 1;
    Wire.write(1);
  }
  
  if (adr == 2) //Test start
    test = true;
  
  if (adr == 3) //LED 
    led = true;
    
  if (adr == 4) //FAN 
    fan = true;
  
   adr=0;
}

void fanf() 
{
  fanstate=!fanstate;
  analogWrite(FAN_PIN, fanstate?255:0);
}

void ledf() 
{
  ledstate=!ledstate;
  digitalWrite(LED_PIN, ledstate);
}




void testf() 
{
  int i, j;

  for(i=0; i<32;i++)
    neostrip.setPixelColor(i, neostrip.gamma32(neostrip.ColorHSV(i * 65536L / 12)));
  neostrip.show();
  delay(2000);

  st=2;
  softSerial.println();
  neostrip.fill(neostrip.Color(255,0,0));
  neostrip.show();
  delay(1000);
  neostrip.fill(neostrip.Color(0, 255,0));
  neostrip.show();
  delay(1000);
  neostrip.fill(neostrip.Color(0,0,255));
  neostrip.show();
  delay(1000);

  st=3;
  softSerial.println();
  for (i = 0; i < 5; i++)
  {
    for (j = 0; j < 3; j++)
    {
      neostrip.fill(neostrip.Color(0, 0, 255), 0, 16);
      neostrip.show();
      delay(100);
      neostrip.fill(0);
      neostrip.show();
      delay(50);
    }
    delay(100);
    for (j = 0; j < 3; j++)
    {
      neostrip.fill(neostrip.Color(255, 0, 0), 16, 16);
      neostrip.show();
      delay(100);
      neostrip.fill(0);
      neostrip.show();
      delay(50);
    }
    delay(100);
  }
  neostrip.fill(0);
  neostrip.show();

  int cnt=0;

  
  for (i = 0; i < 254; i++)
  {
    if (Dynamixel.ping(i) != (-1))
      cnt++;

      st = cnt;
  }


  for(i=1; i<255; i++)
  {
    analogWrite(FAN_PIN, i);
    st=i;
    delay(10);
  }
  
  for(i=255; i>=0; i--)
  {
    analogWrite(FAN_PIN, i);
    st=i;
    delay(10);
  }

    for(i=1; i<255; i++)
  {
    analogWrite(LED_PIN, i);
    st=i;
    delay(10);
  }
  
  for(int i=255; i>=0; i--)
  {
    analogWrite(LED_PIN, i);
    st=i;
    delay(10);
  }
}


void gettemp() 
{
  sensors.requestTemperatures();
  t0 = sensors.getTempC(temp0);
  t1 = sensors.getTempC(temp1);
}


void getsens() 
{
  int i, j;
  float in[2], sum[2];

  in[0] = analogRead(U_PIN);
  in[1] = analogRead(I_PIN);

  for (i = 0; i < 2; i++)
    sum[i] = 0;

  for (i = 0; i < 20; i++)
  {
    if (i == 19)
      for (j = 0; j < 2; j++)
      {
        sens[i][j] = in[j];
        sum[j] = sum[j] + in[j];
      }
    else
      for (j = 0; j < 2; j++)
      {
        sens[i][j] = sens[i + 1][j];
        sum[j] = sum[j] + sens[i][j];
      }
  }

  vol = sum[0] / 20.0 * 0.0151;
  cur = (512.0 - (sum[1] / 20.0)) * 0.0264865;
}
