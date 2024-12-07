from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Adiciona o CORSMiddleware
from pydantic import BaseModel
import serial
import json
import sqlite3
import threading
import time
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do Arduino
arduino_port = "/dev/cu.usbserial-120"  # Atualize conforme necessário
baud_rate = 9600

# Variável global para a conexão serial
arduino = None

def init_serial():
    global arduino
    try:
        if arduino is not None:
            arduino.close()
        
        arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Aguarda a inicialização
        logging.info("Conexão serial estabelecida com sucesso")
        return True
    except serial.SerialException as e:
        logging.error(f"Erro ao inicializar conexão serial: {e}")
        return False

# Tenta estabelecer a conexão inicial
init_serial()

# Banco de dados SQLite
conn = sqlite3.connect("pacotes.db", check_same_thread=False)
cursor = conn.cursor()

# Criação da tabela, se ainda não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS pacotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id TEXT,
    categoria TEXT,
    descricao TEXT,
    peso REAL,
    altura REAL,
    status TEXT,
    timestamp TEXT
)
""")
conn.commit()

# FastAPI
app = FastAPI()

# Adiciona a configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos os domínios
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

class QRCodeData(BaseModel):
    produto_id: str
    categoria: str
    descricao: str
    peso: float
    altura: float

def read_arduino():
    global arduino
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                dados = arduino.readline().decode('utf-8').strip()
                logging.debug(f"Arduino response: {dados}")
        except Exception as e:
            logging.error(f"Erro na leitura serial: {e}")
            # Tenta reinicializar a conexão
            init_serial()
        time.sleep(0.1)

# Inicia a thread de leitura
thread = threading.Thread(target=read_arduino, daemon=True)
thread.start()

@app.post("/produto")
async def processar_qr_code(data: QRCodeData):
    global arduino
    
    try:
        # Verifica se a conexão serial está ativa
        if arduino is None or not arduino.is_open:
            if not init_serial():
                raise HTTPException(status_code=503, 
                                  detail="Conexão serial não disponível")

        # Agora o status depende apenas da categoria
        if data.categoria.lower() in ["smartphones", "tablets"]:
            status = "Válido"
        else:
            status = "Inválido"

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Salva no banco
        cursor.execute(
            "INSERT INTO pacotes (produto_id, categoria, descricao, peso, altura, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data.produto_id, data.categoria, data.descricao, data.peso, data.altura, status, timestamp)
        )
        conn.commit()

        # Prepara mensagem para o Arduino
        mensagem_arduino = {
            "categoria": data.categoria,
            "status": status
        }
        
        # Envia para o Arduino com logging
        msg_string = json.dumps(mensagem_arduino) + "\n"
        logging.debug(f"Enviando para Arduino: {msg_string}")
        
        arduino.write(msg_string.encode())
        arduino.flush()

        return {
            "status": status,
            "message": "Pacote processado",
            "timestamp": timestamp
        }

    except serial.SerialException as e:
        logging.error(f"Erro na comunicação serial: {e}")
        raise HTTPException(status_code=503, 
                          detail="Erro na comunicação com o Arduino")
    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, 
                          detail=str(e))

@app.get("/api/status")
async def get_status():
    cursor.execute("SELECT status, COUNT(*) as count FROM pacotes GROUP BY status")
    rows = cursor.fetchall()
    return [{"name": row[0], "value": row[1]} for row in rows]

@app.get("/api/ultimos_produtos")
async def get_ultimos_produtos():
    # Consulta os 2 últimos produtos processados com base no ID
    cursor.execute("""
        SELECT produto_id, categoria, descricao, peso, altura, status, timestamp 
        FROM pacotes 
        ORDER BY id DESC 
        LIMIT 2
    """)
    rows = cursor.fetchall()

    # Se necessário, podemos adicionar um log para inspeção
    logging.debug(f"Últimos produtos processados: {rows}")

    return [
        {
            "produto_id": row[0],
            "categoria": row[1],
            "descricao": row[2],
            "peso": row[3],
            "altura": row[4],
            "status": row[5],
            "timestamp": row[6]
        }
        for row in rows
    ]

@app.get("/api/total_itens")
async def get_total_itens():
    cursor.execute("SELECT COUNT(*) FROM pacotes")
    total_itens = cursor.fetchone()[0]
    return {"total_itens": total_itens}

@app.get("/api/total_validos")
async def get_total_validos():
    cursor.execute("SELECT COUNT(*) FROM pacotes WHERE status = 'Válido'")
    total_validos = cursor.fetchone()[0]
    return {"total_validos": total_validos}

@app.get("/api/total_invalidos")
async def get_total_invalidos():
    cursor.execute("SELECT COUNT(*) FROM pacotes WHERE status = 'Inválido'")
    total_invalidos = cursor.fetchone()[0]
    return {"total_invalidos": total_invalidos}

@app.get("/api/tempo_medio_analise")
async def get_tempo_medio_analise():
    try:
        # Calcula a diferença entre o timestamp e o momento atual
        cursor.execute("""
            SELECT strftime('%s', 'now') - strftime('%s', timestamp) 
            FROM pacotes
        """)
        tempos = cursor.fetchall()

        if not tempos:
            raise HTTPException(status_code=404, detail="Nenhum pacote encontrado para calcular o tempo")

        # Calcula o tempo médio
        total_tempos = sum([tempo[0] for tempo in tempos])
        media_tempo = total_tempos / len(tempos)

        # Convertendo para segundos, minutos ou outro formato, se necessário
        minutos = media_tempo / 60  # Convertendo para minutos

        return {"tempo_medio_analise": round(minutos, 2)}

    except Exception as e:
        logging.error(f"Erro ao calcular o tempo médio de análise: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular o tempo médio de análise")

@app.get("/api/taxa_sucesso")
async def get_taxa_sucesso():
    try:
        # Consulta o total de pacotes válidos
        cursor.execute("SELECT COUNT(*) FROM pacotes WHERE status = 'Válido'")
        total_validos = cursor.fetchone()[0]

        # Consulta o total de pacotes processados
        cursor.execute("SELECT COUNT(*) FROM pacotes")
        total_pacotes = cursor.fetchone()[0]

        # Evita divisão por zero
        if total_pacotes == 0:
            raise HTTPException(status_code=404, detail="Nenhum pacote encontrado para calcular a taxa de sucesso")

        # Calcula a taxa de sucesso (percentual de pacotes válidos)
        taxa_sucesso = (total_validos / total_pacotes) * 100

        # Retorna a taxa de sucesso com 2 casas decimais
        return {"taxa_sucesso": round(taxa_sucesso, 2)}

    except Exception as e:
        logging.error(f"Erro ao calcular a taxa de sucesso: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular a taxa de sucesso")


@app.get("/api/categories")
async def get_categories():
    cursor.execute("SELECT categoria, COUNT(*) as quantidade FROM pacotes GROUP BY categoria")
    rows = cursor.fetchall()
    return [{"name": row[0], "quantidade": row[1]} for row in rows]

@app.get("/api/time")
async def get_time_data():
    cursor.execute("""
        SELECT strftime('%H:00', timestamp) as hour, COUNT(*) as produtos
        FROM pacotes
        GROUP BY strftime('%H:00', timestamp)
        ORDER BY hour
    """)
    rows = cursor.fetchall()
    return [{"name": row[0], "produtos": row[1]} for row in rows]

@app.on_event("shutdown")
async def shutdown_event():
    global arduino
    if arduino:
        arduino.close()
    conn.close()
