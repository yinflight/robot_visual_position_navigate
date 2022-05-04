//抖音爆改车间主任开源代码
//NN机器人单片机源码
//开发板选择ESP8285
//需要项目-加载库-库管理 中搜索安装FastLED库
//ESP8266 SDK版本为3.0.2
//烧录前先修改Wifi链接信息
//烧录结束后串口监视器查看并记录IP地址
//IO0按键切换 状态灯说明：红色闪烁=wifi链接中，蓝色常亮=视觉控制自动运动，绿色常亮=手动遥控
//转载保留爆改车间主任署名
//关注“爆改车间”微信公众号获取主任更多开关代码
//关注“爆改车间主任”抖音观看主任最新有趣视频

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <FastLED.h>
#define NUM_LEDS 1  
#define DATA_PIN 4
CRGB leds[NUM_LEDS];

unsigned int localPort = 1234;      // 可以自定义端口号
WiFiUDP Udp;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1]; //buffer to hold incoming packet,

#ifndef STASSID
#define STASSID "******"    
#define STAPSK  "******"
#endif
const char* ssid     = STASSID;
const char* password = STAPSK;

const int M1 = 5;
const int M2 = 14;

const int LED =  4;
int BUT = 0;

int power = 256;
int dis,ste,ang,dir;
bool cont;
bool flash;

void LED_red_flash(){
  if(flash){
    leds[0] = CRGB::Red;
    FastLED.show();
    FastLED.show();
  }else{
    leds[0] = CRGB::Black;
    FastLED.show();
    FastLED.show();
  }
  flash = !flash;
}


void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2811, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);
  Serial.println();
  Serial.println();
  Serial.println();
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
  pinMode(BUT, INPUT);
  
  digitalWrite(M1, LOW);
  digitalWrite(M2, LOW);
  
  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    LED_red_flash();
  }

  Serial.println("");
  Serial.println("WiFi connected");
  digitalWrite(LED, HIGH);
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  leds[0] = CRGB::Blue;
  FastLED.show();
  FastLED.show();
  FastLED.show();
  
  Udp.begin(localPort);

}


String templine ="";
void loop() {
  int packetSize = Udp.parsePacket();
  
  if (packetSize) {

    int n = Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    packetBuffer[n] = 0;
    Serial.print("收到数据:");
    Serial.println(packetBuffer);
    Serial.print("发送端IP：");
    Serial.print(Udp.remoteIP().toString().c_str());
    Serial.println(Udp.remotePort());

    String line = packetBuffer;
    String a = packetBuffer;

    if(line.indexOf("M1") != -1){  //左               //接收通道A处理
      turnL();
    }

    if(line.indexOf("M2") != -1){
      turnR();
    }

    if(line.indexOf("MM") != -1){
      forward();
    }
    if(line.indexOf("STOP") != -1){
      stop();
    }

    if(line.indexOf("W") != -1){
      templine=line.substring(line.indexOf("W"));
      power=templine.substring(1,templine.indexOf(",")).toInt();
      Serial.print("power: ");
      Serial.println(power);
    }
    
    if(line.indexOf("C") != -1){
      templine=line.substring(line.indexOf("C"));
      dis=templine.substring(1,templine.indexOf(",")).toInt();
      Serial.print("距离: ");
      Serial.println(dis);
    }

    if(line.indexOf("R") != -1){
      templine=line.substring(line.indexOf("R"));
      ang=templine.substring(1,templine.indexOf(",")).toInt();
      Serial.print("角度: ");
      Serial.println(ang);
    }

    if(line.indexOf("F") != -1){
      templine=line.substring(line.indexOf("F"));
      dir=templine.substring(1,templine.indexOf(",")).toInt();
      Serial.print("方向: ");
      Serial.println(dir);
    }
    
    if(cont == 0){
      if(dis > 25){
        if(ang>160){
          ste = 1;
        }else if( ang<20 and dis <80){
          ste = 1;  
        }else{
          if(dir <0){
            ste = 2;
          }else{
            ste = 3;
          }
        }
      }else{
        ste = 0;
      }

      switch(ste){
        case 0:
          stop();
          break;
        case 1:
          forward();
          break;
        case 2:
          turnR();
          break;
        case 3:
          turnL();
          break;
      }
    }
    
  }


  if(cont){
    leds[0] = CRGB(0,255,0);
    
    FastLED.show();
    FastLED.show();

  }else{
    leds[0] = CRGB(0,0,255);
    FastLED.show();
    FastLED.show();
  }
      
  if(digitalRead(BUT)==LOW){
    delay(20);
    if(digitalRead(BUT)==LOW){
      cont = !cont;
      while(digitalRead(BUT)==LOW);
    }
  }
}

void turnL(){
  analogWrite(M1, power);
  analogWrite(M2, 0);

}

void turnR(){
  analogWrite(M1, 0);
  analogWrite(M2, power);

}

void forward(){
  analogWrite(M1, power);
  analogWrite(M2, power);
}

void stop(){
  analogWrite(M1, 0);
  analogWrite(M2, 0);

}
