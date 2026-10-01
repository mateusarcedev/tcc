# Docker Demo

The software-only application can be started with Docker Compose without installing Python or Node.js on the host.

The Compose configuration is intentionally a **simulation environment**:

- Arduino serial access is disabled;
- no USB device is mounted;
- SQLite data is stored in a named Docker volume;
- the browser-facing dashboard talks to the API on `http://localhost:8000`.

It is not intended to replace the documented native setup for the physical conveyor.

## Requirements

- Docker Engine / Docker Desktop
- Docker Compose v2

## Start API + dashboard

From the repository root:

```bash
docker compose up --build
```

Open:

- dashboard: `http://localhost:3000`
- API health: `http://localhost:8000/api/health`
- Swagger UI: `http://localhost:8000/docs`

## Run the verified demo

With the stack running:

```bash
docker compose --profile tools run --rm demo
```

The demo calls the API through the Compose network and verifies the expected state transition:

```text
+3 total
+2 valid
+1 invalid
```

A successful run ends with:

```text
VERIFY PASSED: API demo produced the expected state transitions.
```

## Stop

```bash
docker compose down
```

To also delete the demo SQLite volume:

```bash
docker compose down -v
```

## Hardware mode

Do not repurpose this Compose file by simply changing `SERIAL_ENABLED=true`.

Physical USB serial access is host- and operating-system-specific. Use the native hardware setup documented in [../Arduino/README.md](../Arduino/README.md) and [hardware.md](hardware.md) so device access and actuator behavior remain explicit.

## Images

The API image:

- runs as a non-root user;
- contains the backend and verification demo script;
- stores runtime SQLite data under `/data`.

The dashboard image:

- builds with the committed lockfile;
- runs as a non-root user;
- embeds `NEXT_PUBLIC_API_URL=http://localhost:8000` at build time for the local browser demo.
