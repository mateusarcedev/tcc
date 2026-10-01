from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import cv2
import requests
from dotenv import load_dotenv
from pyzbar.pyzbar import decode

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/produto")
API_TOKEN = os.getenv("API_TOKEN", "").strip()


def send_to_backend(qr_data: dict[str, Any]) -> dict[str, Any] | None:
    headers = {"X-API-Key": API_TOKEN} if API_TOKEN else {}

    try:
        response = requests.post(
            API_URL,
            json=qr_data,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        logging.info(
            "Package %s processed with status %s",
            qr_data.get("produto_id"),
            result.get("status"),
        )
        return result
    except requests.RequestException as exc:
        logging.error("Backend request failed: %s", exc)
        return None


def read_qr_codes() -> None:
    capture = cv2.VideoCapture(0)
    last_qr = ""

    if not capture.isOpened():
        raise RuntimeError("Unable to open camera index 0")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                continue

            cv2.putText(
                frame,
                "Pressione 'q' para sair",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            for code in decode(frame):
                raw_data = code.data.decode("utf-8")

                if raw_data == last_qr:
                    continue
                last_qr = raw_data

                try:
                    qr_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    logging.warning("Invalid QR JSON ignored")
                    continue

                result = send_to_backend(qr_data)
                if result is None:
                    label = "API indisponivel"
                else:
                    label = f"Status: {result.get('status', 'N/A')}"

                cv2.putText(
                    frame,
                    f"Categoria: {qr_data.get('categoria', 'N/A')}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    label,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

            cv2.imshow("Leitor de QR Code", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    read_qr_codes()
