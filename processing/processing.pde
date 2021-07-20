import controlP5.*;
import processing.net.*;
import ipcapture.*;

IPCapture cam;

Client rpi_cl;

ControlP5 cp5;
Icon ic_con, ic_inc, ic_dec, ic_cam;
Button bt_enc;

PFont iconFont, menuFont, statusFont;

String txt;
float ang=0;
int state=0; //0 - started, 1 - not connected, 2 - connected

boolean cnct=false;
float voltage=0;
String[] menulst={"", "", "", "", ""};
String[] execlst={"", "", "", "", ""};
String menuitem;
String status="";
boolean execshow = false;
boolean bord = false;


void setup() 
{
  size(280, 450);

  iconFont = createFont("fontawesome-webfont.ttf", 30);
  menuFont = createFont("DejaVuSans-Bold.ttf", 30);
  statusFont = createFont("DejaVuSans.ttf", 20);
  cp5 = new ControlP5(this);
  ic_con=cp5.addIcon("connect", 10)
    .setPosition(30, 10)
    .setSize(30, 30)
    .setFont(iconFont)
    .setFontIcons(#00f205, #00f204)
    .setColorForeground(0)
    .setColorActive(0)
    .setSwitch(true)
    ; 
  ic_cam=cp5.addIcon("camera", 10)
    .setPosition(220, 10)
    .setSize(30, 30)
    .setFont(iconFont)
    .setFontIcons(#00f06e, #00f070)
    .setColorForeground(0)
    .setColorActive(0)
    .setSwitch(true)
    ; 
  ic_dec=cp5.addIcon("decr", 10)
    .setPosition(50, 320)
    .setSize(30, 30)
    .setFont(iconFont)
    .setFontIcons(#00f0e2, #00f0e2)
    .setColorForeground(color(128, 128, 128))
    .setColorActive(color(128, 128, 128))
    .setLock(true)
    ; 
  ic_inc=cp5.addIcon("incr", 10)
    .setPosition(200, 320)
    .setSize(30, 30)
    .setFont(iconFont)
    .setFontIcons(#00f01e, #00f01e)
    .setColorForeground(color(128, 128, 128))
    .setColorActive(color(128, 128, 128))
    .setLock(true)
    ; 
  bt_enc=cp5.addButton("encoder")
    .setValue(0)
    .setLabel("")
    .setColorActive(color(0, 100, 255)) 
    .setColorBackground(color(0, 100, 255)) 
    .setColorForeground(color(0, 100, 255))
    .setPosition(123, 338)
    .setSize(34, 34)
    .setLock(true)
    ;

  rectMode(CORNER);
  fill(255);   
  textSize(20);
  textAlign(CENTER);
  txt="Start";
  noStroke();

  state=1;
}


void draw() 
{
  PImage img;
  
  background(220);
  try
  {
    if(cam.isAvailable()) 
      cam.read();
    img=cam;  
    img.resize(736, 416);  
    image(img, 280, 20, 736, 416);
  }
  catch (Exception e) 
  {
  }

  listenwifi();
  if (state!=2)
    cnct=false;

  drawEncoder(ang);

  drawDisplay();

  fill(0);
  textFont(statusFont);

  text(txt, 140, 420);

  if ((state==2)&&(!rpi_cl.active()))
    ic_con.setOff();
}


void listenwifi()
{
  String msg, smsg;

  if (state==2 && rpi_cl.available()>0)
  {
    msg = rpi_cl.readString();

    if (msg.indexOf("<C=")!=-1)
    {
      smsg = msg.substring(msg.indexOf("<C="));
      smsg = smsg.substring(3, smsg.indexOf(">"));
      cnct = smsg.equals("1");
    }
  
    if (msg.indexOf("<V=")!=-1)
    {
      smsg = msg.substring(msg.indexOf("<V="));
      smsg = smsg.substring(3, smsg.indexOf(">"));
      voltage = float(smsg);
    }
    
    if (msg.indexOf("<S=")!=-1)
    {
      smsg = msg.substring(msg.indexOf("<S="));
      smsg = smsg.substring(3, smsg.indexOf(">"));
      status = smsg;
    }
    
    for (int i=0; i<5; i++)
    {
      if (msg.indexOf("<M"+str(i)+"=")!=-1)
      {
        smsg = msg.substring(msg.indexOf("<M"+str(i)+"="));
        smsg = smsg.substring(4, smsg.indexOf(">"));
        menulst[i] = smsg;
        execshow = false;
        bord = false;
      }
    }
    
    for (int i=0; i<5; i++)
    {
      if (msg.indexOf("<E"+str(i)+"=")!=-1)
      {
        smsg = msg.substring(msg.indexOf("<E"+str(i)+"="));
        smsg = smsg.substring(4, smsg.indexOf(">"));
        execlst[i] = smsg;
        execshow = true;
      }
    }
    for (int i=0; i<5; i++)
    {
      if (msg.indexOf("<S"+str(i)+"=")!=-1)
      {
        smsg = msg.substring(msg.indexOf("<S"+str(i)+"="));
        smsg = smsg.substring(4, smsg.indexOf(">"));
        execlst[i] = smsg;
        execshow = true;
        bord = true;
      }
    }

  }
}


void drawDisplay()
{
  fill(0);
  rect(20, 50, 240, 240);

  textAlign(CENTER, CENTER);

  textFont(iconFont);

  if (cnct)
    fill(0, 255, 0);
  else
    fill(128, 128, 128);

  text(char(0xf1eb), 20+30, 50+17); 

  if (voltage > 12)
    fill(0, 255, 0);
  else
  {
    if (voltage > 10)
      fill(255, 255, 0);
    else
      fill(255, 0, 0);
  }

  if (voltage == 0)
    fill(128, 128, 128);

  text(char(0xf1e6), 20+210, 50+17); 

  textFont(menuFont);

  if (execshow)
  {
    for (int i=0; i<5; i++)
    {
      if(i==0)
        fill(255);
      else
        fill(255,255,0);
      if(i==4)
        fill(0,255,0);
      text(execlst[i], 20+120, 50+35+17+i*35);
    }
  } 
  else
  {
    for (int i=0; i<5; i++)
    {
      if (menulst[i].indexOf("#")==0)
      {
        menuitem=menulst[i].substring(1);
        fill(0, 255, 0);
      } else
      {
        menuitem=menulst[i];
        fill(255, 255, 0);
      }
      text(menuitem, 20+120, 50+35+17+i*35);
    }
  }
  
  if(bord)
  {
    noFill();
    stroke(255);
    strokeWeight(5);
    rect(70, 155, 140, 36);
    stroke(0);
    strokeWeight(1);
  }

  textFont(statusFont);
  fill(255);
  text(status, 20+120, 50+210+15);
}


void drawEncoder(float ang)
{
  fill(96);
  circle(140, 355, 100);
  fill(0);
  circle(140, 355, 75); 
  fill(0, 100, 255);
  circle(140, 355, 50);
  pushMatrix();
  translate(140, 355);
  rotate(ang);
  rect(0, 0, 25, 25);
  popMatrix();
}


public void connect(boolean Value)
{
  if (Value && state==1)
  {
    rpi_cl = new Client(this, "192.168.0.114", 11111);

    if (rpi_cl.active())
    {
      txt="Connected";
      ic_inc.setLock(false);
      ic_dec.setLock(false);
      ic_inc.setColorForeground(0);
      ic_dec.setColorForeground(0);
      bt_enc.setLock(false);
      state=2;
    } 
    else
    {
      txt="Not connected";
      ic_con.setOff();
    }
  }

  if (!Value && state==2)
  {
    rpi_cl.stop();
    txt="Disconnected";
    ic_inc.setLock(true);
    ic_dec.setLock(true);
    ic_inc.setColorForeground(color(128, 128, 128));
    ic_dec.setColorForeground(color(128, 128, 128));
    bt_enc.setLock(true);
    ang=0;
    state=1;
    voltage=0;
    for (int i=0; i<5; i++)
      menulst[i]="";
    status="";
  }
}


public void camera(boolean Value)
{
  if(Value)
  {
    surface.setSize(1030,450);
    cam = new IPCapture(this, "http://192.168.0.114:5000/video_feed", "", "");
    cam.start();
    println(cam);
  }
  else
  {
    surface.setSize(280,450);
    cam.stop();
  }
}


public void encoder()
{
  if (state!=0)
    txt="Encoder click";
  if (state==2)
    rpi_cl.write("<2>");
}


public void decr()
{
  ang=ang-PI/10;
  txt="Encoder -";
  if (state==2)
    rpi_cl.write("<-1>");
}


public void incr()
{
  ang=ang+PI/10;
  txt="Encoder +";
  if (state==2)
    rpi_cl.write("<1>");
}


void keyPressed()
{
  if (keyCode==39 && !ic_inc.isLock())
    incr();
  if (keyCode==37 && !ic_dec.isLock())
    decr();
  if (keyCode==40 && !bt_enc.isLock())
    encoder();
}
