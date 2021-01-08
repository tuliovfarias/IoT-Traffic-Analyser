/*
  SD CARD (SPI):
   CS -   pino D8
   DI -   pino D7
   DO -   pino D6
   SCLK - pino D5

  RTC 1307/3231 (I2C)
   SDA/C -   pino D1
   SCL/D -   pino D2

  HC-05 (UART):
   TX -   pino D3
   RX -   pino D4
   PIN32 - pino D0
   VCC -   pino TX (22)

  PUSH BUTTON:
   pino RX (D9,GPIO3)
   GND
*/
//Teste desligar e ligar interrupção e evitar que entre duas vezes nela
#define xt_rsil(level) (__extension__({uint32_t state; __asm__ __volatile__("rsil %0," __STRINGIFY(level) : "=a" (state)); state;}))
#define xt_wsr_ps(state)  __asm__ __volatile__("wsr %0,ps; isync" :: "a" (state) : "memory")

#define MONITOR_SERIAL //Comentar para testar em campo
#define HC_3
//#define TIME 30000 //Tempo para interrupção de timer (ms)

#include <Arduino.h>
#include <SoftwareSerial.h>
#include <EEPROM.h>
#include <SPI.h>
#include <Wire.h> //I2C library
#include <RTClib.h> //RTC library
#include <SD.h>
#include "string.h"
#include <user_interface.h> //Biblioteca do timer
#include "Network.h"

//#define BT_VCC 22   //Alimentação do módulo HC-05 (para ativar modo AT) - *Manual
#define BT_AT D0       //Ligado ao pino 32 do módulo HC-05 (para ativar modo AT)
#define RTC_SDA D1     //Pino de comunicação do RTC
#define RTC_SCL D2     //Clock do RTC
#define SD_CS D8       //Cheep Select do SD card
//#define BT_VCC 10     //Botão usado para iniciar e parar scan

//os_timer_t tmr0;//Cria o Timer. Maximo de 7 Timer's.

SoftwareSerial BTserial(D3, D4); // RX | TX do HC-05
RTC_DS1307 rtc; //RTC_DS3231 rtc;
ESP8266WiFiMulti wifiMulti; 
ESP8266WebServer server(80);

//Protótipos das funções: /////////////////////////////////////////////////////
void error(int);                //Trata erros
void load_flash();               // Carrega variáveis da memória FLASH

void Wifi_config();            //Configura Wifi e HTTP server

void html_config();         //Configura parâmetros do dispositivo (nome, IP)
void html_send();              //Envia arquivo para o Server
void html_monitor();           //Monitoração do dispositivo via server
void html_scan_off();          //Pausa scan do dispositivo

void BT_ATconfig(void);        //Configura Bluetooth e modo AT (HC-05)
void delayAndRead(void);       //Envia comandos AT para o HC-05

void RTC_config(void);         //Configura e verifica erros no RTC
void RTC_log(void);            //Cria string de data e hora atual do RTC

void SD_config();        //Configura e verifica erros no SD card.
void SD_write(char);       //escreve no arquivo do SD. Parametro l=log.

void scan_on_off(void);        //Função da da interrupção do botão de iniciar e parar scan
void get_filename();           //Nome do arquivo no formato YYYY.MM.DD.hh.mm.ss

//Variáveis globais: ///////////////////////////////////////////////////////////

//Variáveis da memória Flash)
char DEVICE_NAME[20]; 
char WIFI_IP[20];    
char WIFI_GATWAY[20];
char WIFI_SUBNET[20];
char WIFI_DNS[20];
//Variáveis da memória RAM
String device;    
String wifi_ip;
String wifi_gatway;
String wifi_subnet;
String wifi_dns;

File dataFile;              //Arquivo .txt para armazenar os dados
File logFile;           //Arquivo .txt para armazenar o log
char r;
char rtc_str[20];           //string que armazena data e hora do rtc
bool play_scan = 1;     //Inicia e para scan
unsigned int i=0;
unsigned int num_scans=0;
String LOG_NAME = "log.txt";
String filename="YYYYMMDD.hhmm.csv";
String str_buffer="";       // armazena dados do BT
String DataString="";
unsigned int files_count=1; //Contador com número de arquivos no SD
unsigned int ok_count=0;

/*void send_to_server(void*z){  //função da interrupção de timer
  Serial.println("AT+INQ\r\n");
  BTserial.println("AT+INQ"); //Inicia scan do HC-05
}*/

void setup() {
  //ESP.wdtDisable(); //(não funciona!)
  //pinMode(BUTTON, INPUT_PULLUP);
#ifdef MONITOR_SERIAL
  Serial.begin(38400);
  while(!Serial);
#endif
  load_flash();
  RTC_config(); //Configura módulo RTC (DataTime)
  SD_config(); //Configura módulo cartão SD
  str_buffer="Initializing " + device + "...\r\n"; SD_write('l');
  str_buffer="SD card module OK\r\n";SD_write('l'); 
  str_buffer="RTC module OK\r\n";SD_write('l');
  Wifi_config();
  str_buffer="WIFI connected to "+WiFi.SSID()+" IP: "+WiFi.localIP().toString()+"\r\n";SD_write('l');
  BT_ATconfig(); //Configura modo AT Bluetooth (HC-05)
  str_buffer="Bluetooth module OK\r\n";SD_write('l');
  logFile.close();
  //attachInterrupt(BUTTON, scan_on_off, FALLING); //Habilita interrupção no PIN_SCAN
  get_filename();
  //os_timer_setfn(&tmr0, send_to_server, NULL); //Indica ao Timer qual sera sua Sub rotina.
  //os_timer_arm(&tmr0,TIME, true); //Inidica ao Timer seu Tempo em mS e se sera repetido ou apenas uma vez 
}
//Main//////////////////////////////////////////////////////////////////////////////////////////
void loop() {
  while (play_scan == 0) {
    server.handleClient();
    ESP.wdtFeed(); //Realimenta WDT
  }
  logFile = SD.open(LOG_NAME, FILE_WRITE);
  str_buffer="SCAN ON\r\n";SD_write('l');
  dataFile = SD.open(filename, FILE_WRITE);
  BTserial.println("AT+INQ"); //Começa scan
  delayAndRead(); str_buffer="";//lê BT para ignorar o OK;
  while (play_scan == 1) {
    server.handleClient();
    //ESP.wdtFeed(); //Realimenta WDT (pode dar erro exception 9)
    while (BTserial.available()) {
      r = BTserial.read(); //Lê char vindo do HC-05
      str_buffer.concat(r);
      if (r == '\n') { // Recebe \r\n no final de cada scan
        SD_write('d'); //Escreve dados com data e hora no SD
        num_scans++;
      }
      else if (r == 'O') { //Reinicia scan após terminar o ciclo (recebe OK)
#ifdef MONITOR_SERIAL
        Serial.println("AT+INQ\r\n");
#endif
    ok_count++;
        BTserial.println("AT+INQ"); //Inicia scan do HC-05
        //delayAndRead(); //Lê o caracter "K" para ignorá-lo
        //break; //para sair do loop while e não gravar "OK"
      }
      //SD_BTdata(); //Grava char no SD
    }
  }
  str_buffer="SCAN OFF\r\n";SD_write('l');
  logFile.close();
  BTserial.println("AT+INQC"); //Pára scan do HC-05
  delayAndRead(); //lê BT para ignorar o OK;
  dataFile.close(); //(Fecha arquivo somente quando pressionado o botão)
}

//Funções: /////////////////////////////////////////////////////////////////////

void delayAndRead()
{
  delay(50); //para esperar a resposta
  while (BTserial.available())
  {
    r = BTserial.read();
    str_buffer.concat(r);
  }
}

void BT_ATconfig(void) {
  // Entrando em modo AT: (SÓ É NECESSÁRIO NA VERSÃO 3.0 DO HC-05)
  #ifdef HC_3
  pinMode(BT_AT, OUTPUT);
  //pinMode(BT_VCC, OUTPUT);
  //digitalWrite(BT_AT, LOW);
  //delay(150);
  //digitalWrite(BT_VCC, LOW);
  digitalWrite(BT_AT, HIGH);
  delay(100);
  //digitalWrite(BT_VCC, HIGH);
  #endif
  BTserial.begin(38400);
  /*//Comandos AT necessários somente na primeira vez (info armazenada na memória FLASH do HC-05):
  //BTserial.println("AT+ORGL");// Restore default status
  //delayAndRead();
  BTserial.println("AT+INIT"); //Inicia biblioteca SSP (só pode ser feito 1 vez)
  delayAndRead();
  BTserial.println("AT+CMODE=1");// Enable connect to any DEVICE_NAME
  delayAndRead();
  BTserial.println("AT+ROLE=1");// modo mestre
  delayAndRead();
  BTserial.println("AT+CLASS=0"); //Encontra qualquer tipo de dispositivo
  delayAndRead();
  BTserial.println("AT+UART=38400,0,0"); //Baud rate, 1 bit de parada, sem paridade
  delayAndRead();*/
  //Comandos AT necessários sempre que ligar: (na v3.0 não são necessários, mantido para identificar erro)
  BTserial.println("AT+INIT"); //Inicia biblioteca SSP (só pode ser feito 1 vez)
  delayAndRead();
  BTserial.println("AT+INQM=1,1000,48"); //RSSI, 100 dispositivos, ~60s
  delayAndRead();  
  if (str_buffer==""){ //se não receber OKs dos comandos AT, aponta erro.
    error(2);
  }
}

void SD_config(void) {
  if (!SD.begin(SD_CS)){
  error(3);
  }
  logFile = SD.open(LOG_NAME, FILE_WRITE);
  if (!logFile) {
    error(4);
  }
}

void RTC_config(void) {
  if (!rtc.begin()) {
    error(0);
  }
  /*if (! rtc.isrunning()) {
    while (1);
  }*/
  rtc.adjust(DateTime(2020, 06, 22, 23, 19, 0)); //ano, mes,dia,hora,minuto,segundo.
}

void SD_write(char log_or_data) {
  //dataFile = SD.open("teste.txt", FILE_WRITE);
  char buf[] = "YYYY/MM/DD hh:mm:ss,";
  DateTime now = rtc.now();   //get the time from the RTC
  DataString=now.toString(buf)+device+","+str_buffer;
  if (log_or_data=='l') logFile.print(DataString); //grava no arquivo de log
  else dataFile.print(DataString); //grava no arquivo de dados
  //dataFile.close();
#ifdef MONITOR_SERIAL
    Serial.print(DataString);
#endif
  str_buffer=""; //limpar str_buffer para receber novos dados
}

/*void ICACHE_RAM_ATTR scan_on_off() {
  uint32_t savedPS = xt_rsil(1); // this routine will allow level 1 and above
  //detachInterrupt(digitalPinToInterrupt(BUTTON));
  //delay(50); //Pode dar erro exepition 9
  if (play_scan == 0)play_scan = 1;
  else play_scan = 0;
  //attachInterrupt(BUTTON, scan_on_off, FALLING); //Habilita interrupção no PIN_SCAN
  xt_wsr_ps(savedPS); // restore the state
}*/

void Wifi_config(){
  IPAddress local_IP; 
  /*IPAddress gateway;    // Set your network Gateway usually your Router base address
  IPAddress subnet;     // Set your network sub-network mask here
  IPAddress dns;        // Set your network DNS usually your Router base address*/
  //Converter strings para IP:
  bool x = local_IP.fromString(wifi_ip); // Define o IP local
  /*x = gateway.fromString(wifi_gateway);
  x = subnet.fromString(wifi_subnet);
  x = subnet.fromString(wifi_dns);*/

  if (!WiFi.config(local_IP, gateway, subnet, dns)) { //WiFi.config(ip, gateway, subnet, dns1, dns2);
    error(1);
  } 
  wifiMulti.addAP(ssid_1, password_1);  // add Wi-Fi networks you want to connect to, it connects strongest to weakest
  while (wifiMulti.run() != WL_CONNECTED) { // Wait for the Wi-Fi to connect: scan for Wi-Fi networks, and connect to the strongest of the networks above
    delay(250); Serial.print('.');
  }
  server.on("/", html_send);
  server.on("/config", html_config);
  server.on("/monitor",html_monitor);
  server.on("/monitor/scan_off",html_scan_off);
  server.begin();
}

void html_send(){ // This gets called twice, the first pass selects the input, the second pass then processes the command line arguments
  dataFile.close(); //É necessário fechar antes de ler
  //logFile=SD.open(LOG_NAME, FILE_WRITE);
#ifdef MONITOR_SERIAL 
  Serial.print("Uplouding file "+filename+"\r\n");
#endif
  //logFile.close();
  dataFile=SD.open(filename);
  if (dataFile){
    Serial.println(millis());////////////////////
    server.sendHeader("Content-Disposition", "attachment; filename="+filename);
    server.streamFile(dataFile, "text/csv");
    Serial.println(millis());////////////////////
    dataFile.close();
  }else;
  get_filename();
  dataFile = SD.open(filename, FILE_WRITE);
  files_count++; //Contador com número de arquivos no SD
}

void html_config(){
  bool flag=0;
  server.sendContent("<!DOCTYPE html><html><style>.font {font-size: 100px;}</style><form class='font' action='/config'><label class='font' for='device'>Device name:</label><input class='font' type='text' name='device' value='"+device+"'><br><br><label class='font' for='ip'>IP:</label><input class='font' type='text' name='ip' value='"+wifi_ip+"'><br><br><input class='font' type='submit' value='Update'></form>");
  for (int i = 0; i < server.args(); i++) { // Só entra se tiver argumentos
    flag=1; //Indica que apertou o botão Update.
    String server_argName = server.argName(i);
    if ((server_argName=="device") & (server.arg("device")!="")){
      device=server.arg("device");
      device.toCharArray(DEVICE_NAME,20); // Necessário, pois a entrada da função EEPROM.put deve ter mesmo tamanho da saída do get.
      EEPROM.put(0,DEVICE_NAME); EEPROM.commit(); //Armazena dados no flash
    }
    else if ((server_argName=="ip") & (server.arg("ip")!="")){
      wifi_ip=server.arg("ip");
      wifi_ip.toCharArray(WIFI_IP,20); // Necessário, pois a entrada da função EEPROM.put deve ter tamanho da saída do get.
      EEPROM.put(20,WIFI_IP); EEPROM.commit(); //Armazena dados no flash
    }
  }
  if(flag==1){
    server.sendContent("<meta http-equiv='refresh' content='0; URL=/monitor' />"); // volta a pagina de monitoração em 0 s
    //html_monitor(); 
  }
}
void html_monitor(){
  /*server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate"); 
  server.sendHeader("Pragma", "no-cache"); 
  server.sendHeader("Expires", "-1"); 
  server.send(200, "text/html", ""); // Empty content inhibits Content-length header so we have to close the socket ourselves. 
  append_page_header();*/
  play_scan=1;
  server.sendContent("<!DOCTYPE html><html><style>.font {font-size: 100px;}</style><h1 class='font'>Device: "+device+"</h1><h1 class='font'>Scans: "+String(num_scans)+"</h1><h1 class='font'>OK count: "+ok_count+"</h1><h1 class='font'>Files: "+(String)files_count+"</h1><br><br><p><a href='/monitor/scan_off'><button class='font'>PAUSAR</button></a></p><br><br><p><a href='/config'><button class='font'>CONFIG</button></a></p></html>");
}

void html_scan_off(){
  play_scan=0;
  server.sendContent("<!DOCTYPE html><html><style>.font {font-size: 100px;}</style><h1 class='font'>Device: "+device+"</h1><h1 class='font'>Scans: "+String(num_scans)+"</h1><h1 class='font'>OK count: "+ok_count+"</h1><h1 class='font'>Files: "+(String)files_count+"</h1><p><a href='/monitor'><button class='font'>INICIAR</button></a></p><br><br><p><a href='/config'><button class='font'>CONFIG</button></a></p></html>");
}
void get_filename(){
  char buf[] = "_YYYYMMDD.hhmm.csv";
  DateTime now = rtc.now();   //get the time from the RTC
  filename = device+now.toString(buf);
  //i++; //teste
}

void load_flash(){
  EEPROM.begin(512); //inicializa gravação na memória flash com 512 bits
  device=EEPROM.get(0,DEVICE_NAME); //pega o nome armazenado no endereço 0 da memória Flash
  wifi_ip=EEPROM.get(20,WIFI_IP); //pega o IP armazenado no endereço 12 da memória Flash
  /*EEPROM.get(24,WIFI_GATWAY);
  wifi_gatway=WIFI_GATWAY;
  EEPROM.get(36,WIFI_SUBNET);
  wifi_subnet=WIFI_SUBNET;
  EEPROM.get(48,WIFI_DNS);
  wifi_dns=WIFI_DNS;*/
}

void error(int error_num){
  switch (error_num){
    case 0:
      str_buffer="ERRO: RTC não iniciou!";SD_write('l');
      break;
    case 1:
      Serial.println(wifi_ip);
      str_buffer="WiFi STATION Failed to configure";SD_write('l');
      break;
    case 2:
      str_buffer="ERRO: Não entrou no modo AT\r\n";SD_write('l');
      break;
    case 3:
      #ifdef MONITOR_SERIAL
      Serial.println("ERRO: SD não iniciou!");
      #endif
      break;
    case 4:
      #ifdef MONITOR_SERIAL
      Serial.println("ERRO: Arquivo não pôde ser criado no SD!");
      #endif
  ;}
  while(1); // force ESP to restart
} 
