#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Wire.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int servoPin1 = 12;
const int servoPin2 = 13;
const int motorPin = 6;

Servo servo1;
Servo servo2;

const int velocidadeEsteira = 190;
const int posEretoServo1 = 90;
const int posEretoServo2 = 0;
const int abaixadoServo1 = 0;
const int abaixadoServo2 = 180;

unsigned long ultimaAcao = 0;
const unsigned long tempoEspera = 3000;

void sendAck(bool ok, const char* produtoId, const char* error = nullptr) {
  StaticJsonDocument<160> response;
  response["ok"] = ok;

  if (produtoId != nullptr) {
    response["produto_id"] = produtoId;
  }

  if (error != nullptr) {
    response["error"] = error;
  }

  serializeJson(response, Serial);
  Serial.println();
}

void desviarPacote(
  Servo& servo,
  int posicaoAbaixada,
  int posicaoEreta,
  const char* mensagem
) {
  lcd.clear();
  lcd.print(mensagem);

  servo.write(posicaoAbaixada);
  delay(2000);
  servo.write(posicaoEreta);

  ultimaAcao = millis();
}

void setup() {
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("Iniciando...");
  delay(1000);

  servo1.attach(servoPin1);
  servo2.attach(servoPin2);

  servo1.write(posEretoServo1);
  servo2.write(posEretoServo2);

  pinMode(motorPin, OUTPUT);
  analogWrite(motorPin, velocidadeEsteira);

  lcd.clear();
  lcd.print("Sistema Pronto!");
  delay(1000);
  lcd.clear();
}

void loop() {
  if (Serial.available() > 0) {
    StaticJsonDocument<256> doc;
    String dados = Serial.readStringUntil('\n');

    DeserializationError error = deserializeJson(doc, dados);

    if (error) {
      lcd.clear();
      lcd.print("Erro JSON");
      sendAck(false, nullptr, "invalid_json");
      return;
    }

    const char* categoria = doc["categoria"];
    const char* status = doc["status"];
    const char* produtoId = doc["produto_id"];

    if (categoria == nullptr || status == nullptr) {
      lcd.clear();
      lcd.print("Dados invalidos");
      sendAck(false, produtoId, "missing_fields");
      return;
    }

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(categoria);
    lcd.setCursor(0, 1);
    lcd.print(status);

    if (strcmp(status, "Válido") == 0) {
      if (strcmp(categoria, "smartphones") == 0) {
        desviarPacote(
          servo1,
          abaixadoServo1,
          posEretoServo1,
          "Smartphone"
        );
      } else if (strcmp(categoria, "tablets") == 0) {
        desviarPacote(
          servo2,
          abaixadoServo2,
          posEretoServo2,
          "Tablet"
        );
      }
    } else {
      lcd.clear();
      lcd.print("Pacote Invalido");
      delay(2000);
    }

    sendAck(true, produtoId);
  }

  if (millis() - ultimaAcao > tempoEspera) {
    lcd.clear();
    lcd.print("Aguardando...");
    ultimaAcao = millis();
  }
}
