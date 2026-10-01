#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Wire.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

constexpr uint8_t SERVO_PIN_1 = 12;
constexpr uint8_t SERVO_PIN_2 = 13;
constexpr uint8_t MOTOR_PWM_PIN = 6;

constexpr uint8_t CONVEYOR_SPEED = 190;
constexpr int SERVO_1_HOME = 90;
constexpr int SERVO_2_HOME = 0;
constexpr int SERVO_1_ROUTE = 0;
constexpr int SERVO_2_ROUTE = 180;

constexpr unsigned long DISPLAY_IDLE_INTERVAL_MS = 3000;

Servo servo1;
Servo servo2;

unsigned long lastActionAt = 0;

void sendAck(bool ok, const char* productId, const char* error = nullptr) {
  JsonDocument response;
  response["ok"] = ok;

  if (productId != nullptr) {
    response["produto_id"] = productId;
  }

  if (error != nullptr) {
    response["error"] = error;
  }

  serializeJson(response, Serial);
  Serial.println();
}

void routePackage(
  Servo& servo,
  int routePosition,
  int homePosition,
  const char* displayMessage
) {
  lcd.clear();
  lcd.print(displayMessage);

  servo.write(routePosition);
  delay(2000);
  servo.write(homePosition);

  lastActionAt = millis();
}

void setup() {
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("Iniciando...");
  delay(1000);

  servo1.attach(SERVO_PIN_1);
  servo2.attach(SERVO_PIN_2);

  servo1.write(SERVO_1_HOME);
  servo2.write(SERVO_2_HOME);

  pinMode(MOTOR_PWM_PIN, OUTPUT);
  analogWrite(MOTOR_PWM_PIN, CONVEYOR_SPEED);

  lcd.clear();
  lcd.print("Sistema Pronto!");
  delay(1000);
  lcd.clear();
}

void loop() {
  if (Serial.available() > 0) {
    JsonDocument doc;
    String input = Serial.readStringUntil('\n');

    DeserializationError error = deserializeJson(doc, input);

    if (error) {
      lcd.clear();
      lcd.print("Erro JSON");
      sendAck(false, nullptr, "invalid_json");
      return;
    }

    const char* category = doc["categoria"];
    const char* status = doc["status"];
    const char* productId = doc["produto_id"];

    if (category == nullptr || status == nullptr) {
      lcd.clear();
      lcd.print("Dados invalidos");
      sendAck(false, productId, "missing_fields");
      return;
    }

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(category);
    lcd.setCursor(0, 1);
    lcd.print(status);

    if (strcmp(status, "Válido") == 0) {
      if (strcmp(category, "smartphones") == 0) {
        routePackage(
          servo1,
          SERVO_1_ROUTE,
          SERVO_1_HOME,
          "Smartphone"
        );
      } else if (strcmp(category, "tablets") == 0) {
        routePackage(
          servo2,
          SERVO_2_ROUTE,
          SERVO_2_HOME,
          "Tablet"
        );
      }
    } else {
      lcd.clear();
      lcd.print("Pacote Invalido");
      delay(2000);
    }

    sendAck(true, productId);
  }

  if (millis() - lastActionAt > DISPLAY_IDLE_INTERVAL_MS) {
    lcd.clear();
    lcd.print("Aguardando...");
    lastActionAt = millis();
  }
}
