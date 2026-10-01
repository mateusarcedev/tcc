from __future__ import annotations

import argparse
from datetime import datetime, timezone

from api import get_connection, init_db

DEMO_PACKAGES = [
    ("DEMO-001", "smartphones", "Smartphone de demonstração", 0.45, 15.0, "Válido"),
    ("DEMO-002", "tablets", "Tablet de demonstração", 0.72, 24.0, "Válido"),
    ("DEMO-003", "livros", "Item fora das categorias aceitas", 0.30, 21.0, "Inválido"),
    ("DEMO-004", "smartphones", "Segundo smartphone de demonstração", 0.50, 16.0, "Válido"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate the local SQLite DB with sanitized demo data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing package rows before inserting demo data.",
    )
    args = parser.parse_args()

    init_db()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with get_connection() as connection:
        if args.reset:
            connection.execute("DELETE FROM pacotes")

        connection.executemany(
            """
            INSERT INTO pacotes
                (produto_id, categoria, descricao, peso, altura, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [(*row, timestamp) for row in DEMO_PACKAGES],
        )

    print(f"Inserted {len(DEMO_PACKAGES)} sanitized demo packages.")


if __name__ == "__main__":
    main()
