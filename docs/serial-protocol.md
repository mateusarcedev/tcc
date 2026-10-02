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
| `version` | Yes | Protocol version. Must be `1`. |
| `command` | Yes | Command name. Must be `sort`. |
| `produto_id` | Yes | Package identifier used to correlate the ACK with the command. |
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

## ACK validation

The API treats a package as hardware-confirmed only when it receives a newline-delimited JSON ACK that:

- parses as a JSON object;
- contains `"ok": true`;
- contains the same `produto_id` sent in the command.

A timeout, malformed response, NACK or mismatched `produto_id` is treated as a hardware communication failure. In that case the API returns HTTP 503 and does not persist the package as successfully processed.

### ACK timing

The current firmware sends the success ACK **after** the routing action finishes. A normal route holds the selected servo in its routing position for about 2 seconds before returning it home, so the backend read timeout must be longer than that physical action.

The default `SERIAL_ACK_TIMEOUT_SECONDS=5` provides headroom over the current ~2 second route. It is configurable because a different conveyor mechanism may require a different completion time. `SERIAL_WRITE_TIMEOUT_SECONDS` controls only the serial write timeout and defaults to 1 second.

Therefore, in protocol version 1, a success ACK means the firmware reached the end of the routing command rather than merely accepting it.

## Compatibility

Protocol version `1` now requires `version`, `command`, `produto_id`, `categoria` and `status`. The stricter contract prevents an unrelated or malformed serial response from being accepted as confirmation.

## Security note

Serial input is considered trusted local input. Network clients must not be given direct access to the serial device. Hardware commands should enter through the API, where validation and optional write authentication are applied.
