#include <ESP8266WiFi.h>       // Built-in
#include <ESP8266WiFiMulti.h>  // Built-in
#include <ESP8266WebServer.h>  // Built-in
#include <ESP8266mDNS.h>

#define   servername "fileserver"     // Set your server's logical name here e.g. if myserver then address is http://myserver.local/
//IPAddress local_IP(192, 168, 1, 152); // Set your server's fixed IP address here - definida na função Wifi_config()
IPAddress gateway(192, 168, 1, 1);    // Set your network Gateway usually your Router base address
IPAddress subnet(255, 255, 255, 0);   // Set your network sub-network mask here
IPAddress dns(192,168,1,1);           // Set your network DNS usually your Router base address

const char ssid_1[]     = "2G TULIO (2)";
const char password_1[] = "1234567890";

const char ssid_2[]     = "2G TULIO";
const char password_2[] = "1234567890";

const char ssid_3[]     = "your_SSID3";
const char password_3[] = "your_PASSWORD_for SSID3";

const char ssid_4[]     = "your_SSID4";
const char password_4[] = "your_PASSWORD_for SSID4";
