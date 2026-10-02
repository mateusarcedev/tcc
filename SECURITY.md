# Security

## Supported use

This repository is an academic hardware + software project. The default configuration is intended for local development and demonstration.

## Runtime data

SQLite databases, logs, environment files, bytecode and common generated artifacts are ignored by Git. Do not commit a live runtime database.

Use:

```bash
python -m api.seed_demo --reset
```

to generate sanitized demonstration records locally.

## API and hardware control

`POST /produto` can result in a physical actuator command when `SERIAL_ENABLED=true`.

For local simulation demos, keep the API bound to loopback. Authentication may remain disabled only while `SERIAL_ENABLED=false`.

When `SERIAL_ENABLED=true`, `API_TOKEN` is mandatory. If it is missing, `POST /produto` fails closed with HTTP 503 before any serial command can be sent. Clients must send the configured token in the `X-API-Key` header.

If the service is exposed beyond the local machine:

- configure a strong `API_TOKEN` and send it in the `X-API-Key` header;
- restrict `CORS_ORIGINS`;
- use HTTPS;
- apply network access control and rate limiting appropriate to the deployment.

Read-only dashboard endpoints do not currently require authentication.

## Reporting

If you find a security issue in this academic project, open a private security report through GitHub when available rather than publishing secrets or exploit details in a public issue.
