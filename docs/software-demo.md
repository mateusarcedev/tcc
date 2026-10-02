# Software-only Demo

This demo proves the main application flow without requiring the physical conveyor, camera or Arduino.

It exercises the real HTTP API, SQLite persistence, validation rules and metrics endpoints.

## Safety behavior

The demo script checks `GET /api/health` before sending packages.

If `SERIAL_ENABLED=true`, it **refuses to continue by default** because `POST /produto` may trigger physical actuators.

Only pass `--allow-hardware` when you intentionally want the demo requests to reach the Arduino.

## Start the API in simulation mode

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
cp .env.example .env
uvicorn api.api:app --host 127.0.0.1 --port 8000
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
Copy-Item .env.example .env
uvicorn api.api:app --host 127.0.0.1 --port 8000
```

The default `.env.example` keeps:

```dotenv
SERIAL_ENABLED=false
```

## Run the verification demo

In another terminal:

```bash
python scripts/demo_api.py --verify
```

The script:

1. verifies API health;
2. records the current total/valid/invalid counters;
3. sends a smartphone package;
4. sends a tablet package;
5. sends an unsupported `livros` package;
6. reads the counters again;
7. verifies the changes are exactly:
   - total: `+3`
   - valid: `+2`
   - invalid: `+1`
8. verifies that software mode reports `serial.mode = simulation`.

A successful run finishes with:

```text
VERIFY PASSED: API demo produced the expected state transitions.
```

## Optional API token

When `API_TOKEN` is configured in the backend, either export the same variable before running the demo or pass:

```bash
python scripts/demo_api.py --verify --api-token "<token>"
```

Do not put real tokens into shell history, documentation or committed files.

## Dashboard

After the API is running:

```bash
cd dashboard
npm ci
npm run dev
```

Open `http://localhost:3000`. Run the demo script again and watch the counters/history update.

## CI proof

GitHub Actions runs the same software demo against a real `uvicorn` process with:

- a temporary SQLite database;
- `SERIAL_ENABLED=false`;
- the same FastAPI application used locally.

This makes the portfolio demo continuously executable even when the physical prototype is not connected.


## Idempotent package processing

`POST /produto` uses `produto_id` as the package idempotency key.

- The first request validates the package, sends the command to the hardware when enabled, waits for a correlated ACK, and persists the result.
- Replaying the same `produto_id` with the same package data returns the original status and timestamp with `"duplicate": true`. It does **not** send another hardware command and does not create another database row.
- Reusing an existing `produto_id` with different package data returns HTTP `409 Conflict`.
- The duplicate check, hardware command, and persistence are serialized in-process so concurrent retries cannot both actuate the conveyor.

The executable demo deliberately replays its first package and verifies that counters still increase only by the three unique demo packages.
