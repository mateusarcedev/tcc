# Arduino firmware

The active firmware is:

```text
Arduino/esteira/esteira.ino
```

Vendored third-party libraries are intentionally not committed. Dependencies are installed through Arduino Library Manager / `arduino-cli`.

## Reproducible dependencies

The CI reference build uses:

| Dependency | Version / source |
| --- | --- |
| Arduino CLI | 1.5.1 |
| Arduino AVR core | current indexed compatible release |
| ArduinoJson | 7.4.3 |
| LiquidCrystal I2C | 1.1.2 |
| Servo | 1.3.0 |
| Wire | Arduino core |

ArduinoJson 7.4.3 is intentionally pinned because it contains the March 2026 buffer-overrun fix.

## Reference compile

The original board model is not present in the historical repository.

CI therefore compiles against **Arduino Uno AVR** only as a portability/reference target:

```bash
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install "ArduinoJson@7.4.3"
arduino-cli lib install "LiquidCrystal I2C@1.1.2"
arduino-cli lib install "Servo@1.3.0"
arduino-cli compile --fqbn arduino:avr:uno Arduino/esteira
```

Passing this build does **not** prove that the original project used an Uno.

## Firmware interfaces

| Component | Configuration |
| --- | --- |
| Servo 1 | digital pin 12 |
| Servo 2 | digital pin 13 |
| Conveyor motor control | PWM pin 6 |
| LCD | I2C address `0x27`, 16x2 |
| Serial | 9600 baud, UTF-8 JSON lines |

## Protocol

See [../docs/serial-protocol.md](../docs/serial-protocol.md).

## Hardware reconstruction

See [../docs/hardware.md](../docs/hardware.md) for the confirmed logical BOM, unknown historical details and wiring diagram.
