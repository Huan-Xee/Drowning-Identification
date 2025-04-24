#define BLINKER_WIFI

#include <Blinker.h>
#include "ESP32_CAM_SERVER.h"

char auth[] = "35ca96c46be3";
char ssid[]="1123";
char pswd[]="11231123";
bool setup_camera = false;

BlinkerButton Button1("btn-abc");
BlinkerNumber Number1("num-abc");
int counter = 0;
int flag = 0;
int32_t rssi_now = 0;

void button1_callback(const String & state)
{
    BLINKER_LOG("get button state: ", state);
    flag++;
    flag /= 2;
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    if(flag){
        Serial.println("warning tunr on");
    }else{
        Serial.println("warning tunr off");
    }
    
}

int32_t check_rssi(){
    static unsigned long lastMillis = 0;
    if (millis() - lastMillis >= 5000) {
        lastMillis = millis();
        
        int32_t rssi = WiFi.RSSI();
        
        // Blinker.print("rssi", rssi);
        
        // Serial.print("信号强度: ");
        // Serial.print(rssi);
        // Serial.println(" dBm");
        return rssi;
    }
}


void dataRead(const String & data)
{
    BLINKER_LOG("Blinker readString: ", data);

    //counter++;
    Number1.print(rssi_now);

    Blinker.vibrate();
    
    uint32_t BlinkerTime = millis();
    
    Blinker.print("millis", BlinkerTime);
}

void setup()
{
    Serial.begin(115200);
    BLINKER_DEBUG.stream(Serial);
    BLINKER_DEBUG.debugAll();

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    
    Blinker.begin(auth, ssid, pswd);
    Blinker.attachData(dataRead);

    Button1.attach(button1_callback);
}

void loop()
{
    Blinker.run();
    rssi_now = check_rssi();
    if (Blinker.connected() && !setup_camera)
    {
        setupCamera();
        setup_camera = true;

        Blinker.printObject("video", "{\"str\":\"mjpg\",\"url\":\"http://"+ WiFi.localIP().toString() + "\"}");
    }
}
