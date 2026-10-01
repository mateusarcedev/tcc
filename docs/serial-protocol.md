# Serial Protocol

## Overview

The FastAPI backend communicates with the Arduino over USB serial.

| Property | Value |
| --- | --- |
| Transport | USB serial |
| Baud rate | 9600 |
| Encoding | UTF-8 |
| Framing | One JSON document per line |
| Protocol version | 1 |
| Direction | API -> Arduino command, Arduino -> API ACK |

A newline (`\n`) terminates every message.

## Command

Example:

```json
{
  "version": 1,
  "command": "sort",
  "produto_id": "DEMO-001",
  "categoria": "smartphones",
  "status": "Válido"
}
```

### Fields

| Field | Required | Description |
| --- | --- | --- |
| `version` | Recommended | Protocol version. Current version: `1`. |
| `command` | Recommended | Command name. Current value: `sort`. |
| `produto_id` | Recommended | Package identifier used for correlation. |
| `categoria` | Yes | Category used to select the routing servo. |
| `status` | Yes | `Válido` or `Inválido`. |

Current routing behavior:

| Category | Action |
| --- | --- |
| `smartphones` | Activate servo 1 |
| `tablets` | Activate servo 2 |
| Other valid strings | No sorting servo |
| Invalid package | Display invalid-package feedback |

## Success ACK

```json
{
  "ok": true,
  "produto_id": "DEMO-001"
}
```

## Error ACK

Malformed JSON:

```json
{
  "ok": false,
  "error": "invalid_json"
}
```

Missing required fields:

```json
{
  "ok": false,
  "produto_id": "DEMO-001",
  "error": "missing_fields"
}
```

## Compatibility

The firmware still bases routing on `categoria` and `status`, so the additional version, command and package identifier fields are forward-compatible with the original command shape.

## Security note

Serial input is considered trusted local input. Network clients must not be given direct access to the serial device. Hardware commands should enter through the API, where validation and optional write authentication are applied.
