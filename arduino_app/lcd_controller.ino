#include <LiquidCrystal_I2C.h>
#include <Wire.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const unsigned long SERIAL_BAUD = 9600;
const String READY_MESSAGE = "LCD_READY";

String readLineFromSerial() {
  static String buffer = "";

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n') {
      String line = buffer;
      buffer = "";
      line.trim();
      return line;
    }

    if (c != '\r') {
      buffer += c;
    }
  }

  return "";
}

void printToLcd(const String &text) {
  String line1 = text.substring(0, 16);
  String line2 = "";

  if (text.length() > 16) {
    line2 = text.substring(16, 32);
  }

  while (line1.length() < 16) line1 += " ";
  while (line2.length() < 16) line2 += " ";

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void setup() {
  Serial.begin(SERIAL_BAUD);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Python LCD App");
  lcd.setCursor(0, 1);
  lcd.print("Hazir...");

  Serial.println(READY_MESSAGE);
}

void loop() {
  String incomingText = readLineFromSerial();

  if (incomingText.length() > 0) {
    printToLcd(incomingText);
    Serial.println("OK");
  }
}
