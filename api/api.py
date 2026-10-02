from __future__ import annotations

import json
import logging
import os
import secrets
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import serial
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SERIAL_ENABLED = env_bool("SERIAL_ENABLED", False)
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/cu.usbserial-120")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "pacotes.db")))
DATABASE_BUSY_TIMEOUT_SECONDS = float(os.getenv("DATABASE_BUSY_TIMEOUT_SECONDS", "10"))
API_TOKEN = os.getenv("API_TOKEN", "").strip()
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

VALID_CATEGORIES = {"smartphones", "tablets"}


class QRCodeData(BaseModel):
    produto_id: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=100)
    descricao: str = Field(min_length=1, max_length=500)
    peso: float = Field(ge=0)
    altura: float = Field(ge=0)


class SerialController:
    """Single owner of the USB serial connection used by the conveyor."""

    def __init__(self) -> None:
        self._connection: serial.Serial | None = None
        self._lock = threading.Lock()

    def connect(self) -> bool:
        if not SERIAL_ENABLED:
            return True

        try:
            if self._connection and self._connection.is_open:
                return True

            self._connection = serial.Serial(
                ARDUINO_PORT,
                BAUD_RATE,
                timeout=1,
                write_timeout=1,
            )
            logging.info(
                "Serial connected on %s at %s baud",
                ARDUINO_PORT,
                BAUD_RATE,
            )
            return True
        except serial.SerialException as exc:
            logging.error("Unable to open serial connection: %s", exc)
            self.close()
            return False

    def send_package(
        self,
        *,
        produto_id: str,
        categoria: str,
        status: str,
    ) -> dict[str, Any]:
        if not SERIAL_ENABLED:
            return {"ok": True, "mode": "simulation"}

        payload = {
            "version": 1,
            "command": "sort",
            "produto_id": produto_id,
            "categoria": categoria,
            "status": status,
        }

        with self._lock:
            if not self.connect() or self._connection is None:
                raise serial.SerialException("serial connection unavailable")

            try:
                message = json.dumps(payload, ensure_ascii=False) + "\n"
                self._connection.write(message.encode("utf-8"))
                self._connection.flush()

                ack_line = self._connection.readline().decode("utf-8").strip()
                if not ack_line:
                    raise serial.SerialException("Arduino ACK timeout")

                try:
                    ack = json.loads(ack_line)
                except json.JSONDecodeError as exc:
                    raise serial.SerialException("invalid Arduino ACK JSON") from exc

                if not isinstance(ack, dict):
                    raise serial.SerialException("invalid Arduino ACK payload")

                if ack.get("ok") is not True:
                    raise serial.SerialException(
                        f"Arduino rejected command: {ack.get('error', 'unknown error')}"
                    )

                ack_product_id = ack.get("produto_id")
                if ack_product_id != produto_id:
                    raise serial.SerialException(
                        "Arduino ACK produto_id does not match command"
                    )

                return ack
            except (serial.SerialException, OSError):
                self.close()
                raise

    def close(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:
                logging.exception("Error closing serial connection")
            finally:
                self._connection = None


serial_controller = SerialController()
package_processing_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=DATABASE_BUSY_TIMEOUT_SECONDS,
    )
    connection.row_factory = sqlite3.Row
    connection.execute(
        f"PRAGMA busy_timeout = {int(DATABASE_BUSY_TIMEOUT_SECONDS * 1000)}"
    )
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pacotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                peso REAL NOT NULL,
                altura REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )


def require_write_key(x_api_key: str | None = Header(default=None)) -> None:
    if not API_TOKEN:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid API key")


def package_status(category: str) -> str:
    return "Válido" if category.strip().lower() in VALID_CATEGORIES else "Inválido"


init_db()

app = FastAPI(
    title="Conveyor QR Automation API",
    version="1.0.0",
    description="Backend for QR validation, persistence and Arduino conveyor control.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
    except sqlite3.Error as exc:
        logging.error("Database health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {
        "status": "ok",
        "database": "ok",
        "serial_enabled": SERIAL_ENABLED,
        "serial_mode": "hardware" if SERIAL_ENABLED else "simulation",
    }


@app.post("/produto")
async def processar_qr_code(
    data: QRCodeData,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict[str, Any]:
    require_write_key(x_api_key)

    normalized_category = data.categoria.strip().lower()
    status = package_status(normalized_category)

    # BEGIN IMMEDIATE obtains SQLite's write reservation before the duplicate
    # check. Together with the in-process lock, this serializes package
    # processing across threads, workers and API instances sharing this DB.
    try:
        with package_processing_lock:
            with get_connection() as connection:
                connection.execute("BEGIN IMMEDIATE")

                existing = connection.execute(
                    """
                    SELECT produto_id, categoria, descricao, peso, altura, status, timestamp
                    FROM pacotes
                    WHERE produto_id = ?
                    ORDER BY id ASC
                    LIMIT 1
                    """,
                    (data.produto_id,),
                ).fetchone()

                if existing is not None:
                    same_payload = (
                        existing["categoria"].strip().lower() == normalized_category
                        and existing["descricao"] == data.descricao
                        and float(existing["peso"]) == data.peso
                        and float(existing["altura"]) == data.altura
                    )
                    if not same_payload:
                        raise HTTPException(
                            status_code=409,
                            detail="produto_id already exists with different package data",
                        )

                    return {
                        "status": existing["status"],
                        "message": "Pacote já processado",
                        "timestamp": existing["timestamp"],
                        "duplicate": True,
                        "serial": {"ok": True, "mode": "idempotent_replay"},
                    }

                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                try:
                    serial_ack = serial_controller.send_package(
                        produto_id=data.produto_id,
                        categoria=normalized_category,
                        status=status,
                    )
                except serial.SerialException as exc:
                    logging.error("Serial communication failed: %s", exc)
                    raise HTTPException(
                        status_code=503,
                        detail="Hardware controller unavailable",
                    ) from exc

                connection.execute(
                    """
                    INSERT INTO pacotes
                        (produto_id, categoria, descricao, peso, altura, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data.produto_id,
                        normalized_category,
                        data.descricao,
                        data.peso,
                        data.altura,
                        status,
                        timestamp,
                    ),
                )
    except sqlite3.OperationalError as exc:
        logging.error("Database transaction failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable",
        ) from exc

    return {
        "status": status,
        "message": "Pacote processado",
        "timestamp": timestamp,
        "duplicate": False,
        "serial": serial_ack,
    }


@app.get("/api/status")
async def get_status() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT status, COUNT(*) AS count FROM pacotes GROUP BY status"
        ).fetchall()
    return [{"name": row["status"], "value": row["count"]} for row in rows]


@app.get("/api/ultimos_produtos")
async def get_ultimos_produtos() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT produto_id, categoria, descricao, peso, altura, status, timestamp
            FROM pacotes
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/total_itens")
async def get_total_itens() -> dict[str, int]:
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM pacotes").fetchone()[0]
    return {"total_itens": total}


@app.get("/api/total_validos")
async def get_total_validos() -> dict[str, int]:
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM pacotes WHERE status = 'Válido'"
        ).fetchone()[0]
    return {"total_validos": total}


@app.get("/api/total_invalidos")
async def get_total_invalidos() -> dict[str, int]:
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM pacotes WHERE status = 'Inválido'"
        ).fetchone()[0]
    return {"total_invalidos": total}


@app.get("/api/taxa_sucesso")
async def get_taxa_sucesso() -> dict[str, float]:
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM pacotes").fetchone()[0]
        validos = connection.execute(
            "SELECT COUNT(*) FROM pacotes WHERE status = 'Válido'"
        ).fetchone()[0]

    taxa = 0.0 if total == 0 else (validos / total) * 100
    return {"taxa_sucesso": round(taxa, 2)}


@app.get("/api/categories")
async def get_categories() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT categoria, COUNT(*) AS quantidade
            FROM pacotes
            GROUP BY categoria
            ORDER BY quantidade DESC
            """
        ).fetchall()
    return [{"name": row["categoria"], "quantidade": row["quantidade"]} for row in rows]


@app.get("/api/time")
async def get_time_data() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT strftime('%H:00', timestamp) AS hour, COUNT(*) AS produtos
            FROM pacotes
            GROUP BY strftime('%H:00', timestamp)
            ORDER BY hour
            """
        ).fetchall()
    return [{"name": row["hour"], "produtos": row["produtos"]} for row in rows]


@app.on_event("shutdown")
async def shutdown_event() -> None:
    serial_controller.close()
