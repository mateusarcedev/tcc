# Arduino firmware

The active firmware is:

```text
Arduino/esteira/esteira.ino
```

Vendored copies of third-party Arduino libraries were removed from the repository. Install dependencies using Arduino IDE Library Manager or `arduino-cli`.

## Libraries

- Servo — Arduino built-in/core library for supported boards
- Wire — Arduino built-in/core I2C library
- ArduinoJson
- LiquidCrystal I2C

## Hardware assumptions

The current sketch expects:

| Component | Configuration |
| --- | --- |
| Servo 1 | pin 12 |
| Servo 2 | pin 13 |
| Conveyor motor PWM | pin 6 |
| LCD | I2C address `0x27`, 16x2 |
| Serial | 9600 baud |

The exact Arduino board/FQBN is not recorded in the historical repository. Add it here once confirmed so the firmware can be compiled in CI with `arduino-cli`.

See [../docs/serial-protocol.md](../docs/serial-protocol.md) for the serial message contract.
