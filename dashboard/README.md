# Web dashboard

Next.js dashboard for the conveyor automation project.

It reads metrics and recent package events from the FastAPI backend.

## Configuration

Set:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Development

```bash
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

The API must be running separately.

## Data sources

The dashboard uses:

- `GET /api/total_itens`
- `GET /api/total_validos`
- `GET /api/total_invalidos`
- `GET /api/taxa_sucesso`
- `GET /api/status`
- `GET /api/categories`
- `GET /api/time`
- `GET /api/ultimos_produtos`

Do not deploy an outdated Next.js lockfile. Before public deployment, install the current patched dependency set and run `npm audit --omit=dev` and `npm run build`.
