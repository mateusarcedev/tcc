  #include <Servo.h>
  #include <Wire.h>
  #include <LiquidCrystal_I2C.h>
  #include <ArduinoJson.h>

  // Inicializa o display LCD
  LiquidCrystal_I2C lcd(0x27, 16, 2);

  // Configuração dos pinos
  const int servoPin1 = 12;  // Servo para smartphones
  const int servoPin2 = 13;  // Servo para tablets
  const int motorPin = 6;    // Motor da esteira

  Servo servo1, servo2;
  int velocidadeEsteira = 190;

  // Posições dos servos
  const int posEretoServo1 = 90;
  const int posEretoServo2 = 0;
  const int abaixadoServo1 = 0;
  const int abaixadoServo2 = 180;

  // Variáveis de controle
  unsigned long ultimaAcao = 0;
  const unsigned long tempoEspera = 3000; // 3 segundos

  void setup() {
    // Inicializa comunicação serial
    Serial.begin(9600);
    
    // Inicializa LCD
    lcd.init();
    lcd.backlight();
    lcd.clear();
    lcd.print("Iniciando...");
    delay(1000);
    
    // Configuração dos servos
    servo1.attach(servoPin1);
    servo2.attach(servoPin2);
    
    // Posição inicial dos servos
    servo1.write(posEretoServo1);
    servo2.write(posEretoServo2);
    
    // Configuração do motor
    pinMode(motorPin, OUTPUT);
    analogWrite(motorPin, velocidadeEsteira);
    
    lcd.clear();
    lcd.print("Sistema Pronto!");
    delay(1000);
    lcd.clear();
  }

  void desviarPacote(Servo &servo, int posicaoAbaixada, int posicaoEreta, const char* mensagem) {
    lcd.clear();
    lcd.print(mensagem);
    
    servo.write(posicaoAbaixada);
    delay(2000);  // Aguarda o desvio
    servo.write(posicaoEreta);
    
    // Atualiza o timestamp da última ação
    ultimaAcao = millis();
  }

  void loop() {
    if (Serial.available() > 0) {
      // Buffer para receber os dados
      StaticJsonDocument<200> doc;
      String dados = Serial.readStringUntil('\n');
      
      // Parse do JSON
      DeserializationError error = deserializeJson(doc, dados);
      
      if (error) {
        lcd.clear();
        lcd.print("Erro JSON");
        return;
      }
      
      // Extrai os dados
      const char* categoria = doc["categoria"];
      const char* status = doc["status"];
      
      // Mostra no LCD
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(categoria);
      lcd.setCursor(0, 1);
      lcd.print(status);
      
      // Processa apenas se o status for válido
      if (strcmp(status, "Válido") == 0) {
        if (strcmp(categoria, "smartphones") == 0) {
          desviarPacote(servo1, abaixadoServo1, posEretoServo1, "Smartphone");
        }
        else if (strcmp(categoria, "tablets") == 0) {
          desviarPacote(servo2, abaixadoServo2, posEretoServo2, "Tablet");
        }
      } else {
        lcd.clear();
        lcd.print("Pacote Invalido");
        delay(2000);
      }
    }
    
    // Se passou muito tempo desde a última ação, limpa o display
    if (millis() - ultimaAcao > tempoEspera) {
      lcd.clear();
      lcd.print("Aguardando...");
      ultimaAcao = millis();
    }
  }