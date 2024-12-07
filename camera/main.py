import cv2
import requests
import json
import time
from pyzbar.pyzbar import decode
import serial
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações
API_URL = "http://localhost:8000/produto"
ARDUINO_PORT = "/dev/cu.usbserial-120"
BAUD_RATE = 9600

class ArduinoController:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.connect()

    def connect(self):
        try:
            if self.serial is not None:
                self.serial.close()
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Aguarda inicialização
            logging.info("Conexão serial estabelecida com sucesso")
            return True
        except serial.SerialException as e:
            logging.error(f"Erro ao conectar com Arduino: {e}")
            return False

    def send_command(self, category, status):
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                logging.error("Não foi possível enviar comando - Arduino não conectado")
                return False

        try:
            command = {
                "categoria": category,
                "status": status
            }
            msg = json.dumps(command) + "\n"
            self.serial.write(msg.encode())
            self.serial.flush()
            logging.debug(f"Comando enviado para Arduino: {msg.strip()}")
            return True
        except Exception as e:
            logging.error(f"Erro ao enviar comando: {e}")
            return False

    def close(self):
        if self.serial:
            self.serial.close()

def salvar_no_backend(qr_data):
    try:
        # Envia os dados para o backend (registro no dashboard)
        response = requests.post(API_URL, json=qr_data)
        if response.status_code == 200:
            logging.info(f"Dados salvos no backend: {qr_data}")
        else:
            logging.warning(f"Erro ao salvar no backend: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Erro de conexão com backend: {e}")

def ler_qrcode():
    # Inicializa a câmera
    cap = cv2.VideoCapture(0)
    ultimo_qr = ""
    
    # Inicializa o controle do Arduino
    arduino = ArduinoController(ARDUINO_PORT, BAUD_RATE)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Adiciona texto informativo na imagem
            cv2.putText(frame, "Pressione 'q' para sair", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            for code in decode(frame):
                dados = code.data.decode("utf-8")
                if dados != ultimo_qr:
                    ultimo_qr = dados
                    logging.info(f"Novo QR Code detectado: {dados}")

                    try:
                        # Decodifica o JSON do QR Code
                        qr_data = json.loads(dados)

                        # Depuração: Imprime a categoria detectada
                        categoria_detectada = qr_data.get('categoria', '')
                        logging.debug(f"Categoria detectada: {categoria_detectada}")
                        
                        # Verifica a categoria e define o status
                        if categoria_detectada.lower() in ["smartphones", "tablets"]:
                            status = "Válido"
                        else:
                            status = "Inválido"
                        
                        # Adiciona o campo de status no JSON antes de enviar para o Arduino
                        qr_data["status"] = status

                        # Depuração: Mostra o status atribuído
                        logging.debug(f"Status atribuído: {status}")

                        # Se o status for Válido, envia comando para o Arduino
                        if status == "Válido":
                            arduino.send_command(categoria_detectada, status)
                        
                        # Mostra feedback visual
                        cv2.putText(frame, f"Categoria: {qr_data.get('categoria', 'N/A')}", 
                                  (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Status: {status}", 
                                  (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        # Sempre salva os dados no backend, independentemente do status
                        salvar_no_backend(qr_data)

                    except json.JSONDecodeError:
                        logging.error(f"QR Code inválido: {dados}")
                        continue
                    except Exception as e:
                        logging.error(f"Erro ao processar QR Code: {e}")
                        continue

            cv2.imshow("Leitor de QR Code", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        arduino.close()

if __name__ == "__main__":
    ler_qrcode()
