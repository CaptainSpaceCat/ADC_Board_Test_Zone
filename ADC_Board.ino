#include <SPI.h>
#define chipSelectPin 3
#define startSync 9
#define resetPin 8

//https://raw.githubusercontent.com/sparkfun/Arduino_Boards/master/IDE_Board_Manager/package_sparkfun_index.json
//https://adafruit.github.io/arduino-board-index/package_adafruit_index.json 
//use python script to save to file
//const int TX_LED = PIN_LED_TXL;  //SAMD21 green LED
//const int RX_LED = PIN_LED_RXL;  //SAMD21 yellow LED
bool PGAen = false;
bool startUP = false;
bool resetMe= false;
bool printData = true;
byte address, thisValue, address2, address3 = 0;
byte readOut0, readOut1, readOut2, readOut3, readOut4, readOut5, readOut6, readOut7, readOut8, readOut9, readOut10, readOut11, readOut12, readOut13, readOut14, readOut15, readOut16, readOut17 = 0;
byte inByte1, inByte2, inByte3 = 0;

unsigned long timer = 0;


/*------------------------------------------------*/
/*---------- varriables you need to set! ---------*/ 
const float refV = 2.5; //reference voltage for the ADC. Usually use internal 2.5V by setting the registers below
const float pgaGain = 1;
const float FSR = (refV*2)/pgaGain;
const float LSBsize = FSR/pow(2,24);
bool showHex = true;
long loopTime = 10;   // microseconds
/*------------------------------------------------*/
/*------------------------------------------------*/



void setup() {
  Serial.begin(115200);
  delay(3);
//  pinMode(RX_LED, OUTPUT);
//  pinMode(TX_LED, OUTPUT);
  Serial.println("Serial Connected");
  pinMode(resetPin,OUTPUT);
  pinMode(chipSelectPin,OUTPUT); 
  pinMode(startSync,OUTPUT); 
  digitalWrite(startSync, HIGH);
  digitalWrite(resetPin, HIGH);
  delayMicroseconds(1);
  delay(500);
  SPI.begin();
  //SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE1);
  
  
  /* inital startup routine (including reset)*/ 
  delay(100);
  resetADC();
  delay(1000); 

  /* register configuration - use excel calculator!*/
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x42);   //Send register START location
  SPI.transfer(0x07);   //how many registers to write to
  SPI.transfer(0xBA);   //0x42  INPMUX 
  SPI.transfer(0x08);   //0x43  PGA
  SPI.transfer(0x99);   //0x44  DATARATE chop w/ 200 SPS
  SPI.transfer(0x39);   //0x45  REF
  SPI.transfer(0x00);   //0x46  IDACMAG
  SPI.transfer(0xFF);   //0x47  IDACMUX
  SPI.transfer(0x00);   //0x48  VBIAS
  SPI.transfer(0x18);   //0x49  SYS
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  delay(3000);
  
  startADC();
  delay(100);

  /*Read all the register values*/ 
//  IDAC(true, 0x02, 0xF8); 
  delay(1000);
  delay(50);
  SFOCAL();
  delay(5);
  
  timer = micros();
//  Serial.print("LSB size ");Serial.println(LSBsize,DEC);


}






/*------------------------------------------------*/
/*------------------------------------------------*/
void loop() {
  timeSync(loopTime);

  //check command interrupt
  if (Serial.available() > 0) {
    handleCommand();
  }

  /* HALL SPIN -- A --*/
  float rDataA = 0;
  writeReg(0x42, 0x60); 
  delay(5);
  writeReg(0x48, 0x08); 
  delay(5);
  IDAC(true, 0x04, 0xF2); 
//  delay(50);
//  SFOCAL();
  delay(20);
  rDataA = readData1(showHex = false, 1, printData = false);
 
 /* HALL SPIN -- B --*/
  float rDataB = 0;
  writeReg(0x42, 0x23); 
  delay(5);
  writeReg(0x48, 0x01); 
  delay(20);
  IDAC(true, 0x04, 0xF6); 
//  delay(50);
//  SFOCAL();
  delay(5);
  rDataB = readData1(showHex = false, 1, printData = false);
  float dataSpin = (rDataA-rDataB)*1;
  Serial.print(micros());
  Serial.print(",");
  Serial.println(dataSpin, DEC);






}
/*------------------------------------------------*/









void handleCommand() {
  String command = "";
  while (Serial.available() > 0) {
    byte inByte = Serial.read();
    command += (char)inByte;
  }
  command = command.substring(0, command.length() - 1);
  Serial.println(command);

  
}

void sendToPC(byte* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}

void timeSync(unsigned long deltaT)
{
  unsigned long currTime = micros();
  long timeToDelay = deltaT - (currTime - timer);
  if (timeToDelay > 5000)
  {
    delay(timeToDelay / 1000);
    delayMicroseconds(timeToDelay % 1000);
  }
  else if (timeToDelay > 0)
  {
    delayMicroseconds(timeToDelay);
  }
  else
  {
      // timeToDelay is negative so we start immediately
  }
  timer = currTime + timeToDelay;
}

/*Start ADC with command + SYNC pin --- WORKING ---*/
void startADC() {
  Serial.println("---Starting ADC---");
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x08); //send start byte
  digitalWrite(startSync, LOW);
  delay(4*1/10000000);
  digitalWrite(startSync, HIGH);
  delay(20);
  digitalWrite(chipSelectPin, HIGH);
}

/*Stop ADC with command + SYNC pin --- UNKNOWN ---*/
void stopADC() {
  Serial.println("---Stopping ADC---");
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x0A); //send start byte
  digitalWrite(startSync, LOW);
  delay(20);
  digitalWrite(chipSelectPin, HIGH);
}

/*Configure current excitation source --- WORKING ---*/
void IDAC(bool setIDAC, byte valIDAC, byte pinIDAC){
  if(setIDAC == 1){
    digitalWrite(chipSelectPin, LOW);
    SPI.transfer(0x46);   //Send register START location
    SPI.transfer(0x01);   //how many registers to write to
    SPI.transfer(valIDAC);   //set 0x46 register to ENABLE @ 100uA
    SPI.transfer(pinIDAC);   //set register to specified value
    delay(1);
    digitalWrite(chipSelectPin, HIGH); 
    }
  else{
    digitalWrite(chipSelectPin, LOW);
    SPI.transfer(0x46);   //Send register START location
    SPI.transfer(0x01);   //how many registers to write to
    SPI.transfer(0x00);   //set 0x46 register to DISABLE
    SPI.transfer(0xFF);   //set 0x47 register to DISCONNECT all IDAC pins
    delay(1);
    digitalWrite(chipSelectPin, HIGH);
    }
}

/*Reset ADC with command + reset pin --- WORKING ---*/
void resetADC() {
  Serial.println("---Resetting ADC---");
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x06); //send reset byte
  digitalWrite(resetPin, LOW);
  delay(4*1/10000000);
  digitalWrite(resetPin, HIGH);
  delay(4096*1/10000000);
  digitalWrite(chipSelectPin, HIGH); 
}

/*Read 24 bit data from ADC --- WORKING ---*/
float readData1(bool showHex, int scalar, bool printData) { //read the ADC data when STATUS and CRC bits are NOT enabled
//  Serial.print("Data Read: ");
  float decVal = 0;
  /*Read the three bytes of 2's complement data from the ADC*/ 
  digitalWrite(chipSelectPin, LOW);  
  SPI.transfer(0x12); //transfer read command  
  inByte1 = SPI.transfer(0x00);
  inByte2 = SPI.transfer(0x00);
  inByte3 = SPI.transfer(0x00);
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  
  /*Convert the three bytes into readable data*/
  int rawData = 0; //create an empty 24 bit integer for the data
  rawData = (rawData << 8) | inByte1; //shift the data in one byte at a time
  rawData = (rawData << 8) | inByte2;
  rawData = (rawData << 8) | inByte3;
  
  /*Print the HEX value (if showHex = true)*/
  if (showHex == 1){
    Serial.print("HEX Value: ");
    Serial.println(rawData,HEX);
  }
  if (((1 << 23) & rawData) != 0){ //check if the value is negative    
    int mask = (1 << 24) - 1;
    int result = ((~rawData) & mask) + 1;
    decVal = float(result) * scalar * LSBsize * -1;
  }

  else{ //if it's not negative
    decVal = float(rawData)*LSBsize*scalar; //then just multiply by LSBsize
  }
//  Serial.println(decVal, DEC);
  if (printData == 1){Serial.println(decVal,DEC);}
  return decVal;
}


/*Read internal temperature --- NOT WORKING ---*/
void readTemp() {
  writeReg(0x43, 0x0A); //set PGA gain to 4 
  delay(20);
  writeReg(0x49, 0x50); //enable internal temp monitor
  delay(500);
  float a = readData1(showHex = false, 1000, printData = false);
  Serial.print(0.1*a*(1/0.403)), Serial.println(" degrees C");
  delay(5);
  writeReg(0x49, 0x18); //disable internal temp monitor
  delay(500);  
}

/*Write register value --- WORKING ---*/
void writeReg(byte address, byte thisValue) {
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(address); //Send register location
  SPI.transfer(0x00);
  SPI.transfer(thisValue);  //Send value to write 
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  address = 0;
  thisValue = 0;
}

/*Read register value --- UNKNOWN ---*/
void readReg(byte address2) {  
  byte inByte = 0x00;
  byte result = 0x00;
  byte rawRegVal = 0x00;
  Serial.print(address2, HEX);
  Serial.print("\t");
  digitalWrite(chipSelectPin, LOW); 
  SPI.transfer(address2);
  inByte = SPI.transfer(0x00);
  result = SPI.transfer(0x00);
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  rawRegVal = (rawRegVal << 8 | result);
  Serial.print(rawRegVal, HEX);
  Serial.print("\t");
  Serial.println(result, HEX);
}


/*Read ALL of the registers in a row --- WORKING ---*/
void regReadout(){
  Serial.println("------Register Readout-------");
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x20);   //Send register START location
  SPI.transfer(0x12);   //how many registers we want to read (0x12 = all 18)
  readOut0 = SPI.transfer(0x00);
  readOut1 = SPI.transfer(0x00);
  readOut2 = SPI.transfer(0x00);
  readOut3 = SPI.transfer(0x00);
  readOut4 = SPI.transfer(0x00);
  readOut5 = SPI.transfer(0x00);
  readOut6 = SPI.transfer(0x00);
  readOut7 = SPI.transfer(0x00);
  readOut8 = SPI.transfer(0x00);
  readOut9 = SPI.transfer(0x00);
  readOut10 = SPI.transfer(0x00);
  readOut11 = SPI.transfer(0x00);
  readOut12 = SPI.transfer(0x00);
  readOut13 = SPI.transfer(0x00);
  readOut14 = SPI.transfer(0x00);
  readOut15 = SPI.transfer(0x00);
  readOut16 = SPI.transfer(0x00);
  readOut17 = SPI.transfer(0x00);  
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  Serial.print("Register 0x00 (ID):        "), Serial.println(readOut0, HEX);
  Serial.print("Register 0x01 (STATUS):    "), Serial.println(readOut1, HEX);
  Serial.print("Register 0x02 (INPMUX):    "), Serial.println(readOut2, HEX);
  Serial.print("Register 0x03 (PGA):       "), Serial.println(readOut3, HEX);
  Serial.print("Register 0x04 (DATARATE):  "), Serial.println(readOut4, HEX);
  Serial.print("Register 0x05 (REF):       "), Serial.println(readOut5, HEX);
  Serial.print("Register 0x06 (IDACMAG):   "), Serial.println(readOut6, HEX);
  Serial.print("Register 0x07 (IDACMUX):   "), Serial.println(readOut7, HEX);
  Serial.print("Register 0x08 (VBIAS):     "), Serial.println(readOut8, HEX);
  Serial.print("Register 0x09 (SYS):       "), Serial.println(readOut9, HEX);
  Serial.print("Register 0x0A (OFCAL0):    "), Serial.println(readOut10, HEX);
  Serial.print("Register 0x0B (OFCAL1):    "), Serial.println(readOut11, HEX);
  Serial.print("Register 0x0C (OFCAL2):    "), Serial.println(readOut12, HEX);
  Serial.print("Register 0x0D (FSCAL0):    "), Serial.println(readOut13, HEX);
  Serial.print("Register 0x0E (FSCAL1):    "), Serial.println(readOut14, HEX);
  Serial.print("Register 0x0F (FSCAL2):    "), Serial.println(readOut15, HEX);
  Serial.print("Register 0x10 (GPIODAT):   "), Serial.println(readOut16, HEX);
  Serial.print("Register 0x11 (GPIOCON):   "), Serial.println(readOut17, HEX);
  Serial.println("-----------------------------");
}

/*Initiate Self Calibration --- UNKNOWN ---*/
void SFOCAL() {
//  Serial.println("Self Calibration");
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(0x19); //send self offset command
  delay(1);
  digitalWrite(chipSelectPin, HIGH);
  delay(100);
}

/*Hall Switching --- UNKNOWN ---*/
//void hallSwitch() {
//  
//}
