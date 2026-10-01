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

For local demos, keep the API bound to loopback.

If the service is exposed beyond the local machine:

- set `API_TOKEN` and send it in the `X-API-Key` header;
- restrict `CORS_ORIGINS`;
- use HTTPS;
- apply network access control and rate limiting appropriate to the deployment.

Read-only dashboard endpoints do not currently require authentication.

## Reporting

If you find a security issue in this academic project, open a private security report through GitHub when available rather than publishing secrets or exploit details in a public issue.
