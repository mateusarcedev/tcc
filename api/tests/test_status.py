import json
import os
import unittest
from unittest.mock import patch

os.environ["SERIAL_ENABLED"] = "false"
os.environ["DATABASE_PATH"] = ":memory:"

import serial  # noqa: E402

import api.api as api_module  # noqa: E402
from api.api import SerialController, package_status, require_write_key  # noqa: E402


class PackageStatusTests(unittest.TestCase):
    def test_smartphones_are_valid(self) -> None:
        self.assertEqual(package_status("smartphones"), "Válido")

    def test_tablets_are_valid_case_insensitively(self) -> None:
        self.assertEqual(package_status("  TABLETS  "), "Válido")

    def test_other_categories_are_invalid(self) -> None:
        self.assertEqual(package_status("livros"), "Inválido")


class WriteAuthenticationTests(unittest.TestCase):
    def test_simulation_allows_missing_token_for_local_demo(self) -> None:
        with (
            patch.object(api_module, "SERIAL_ENABLED", False),
            patch.object(api_module, "API_TOKEN", ""),
        ):
            require_write_key(None)

    def test_hardware_mode_refuses_to_run_without_configured_token(self) -> None:
        with (
            patch.object(api_module, "SERIAL_ENABLED", True),
            patch.object(api_module, "API_TOKEN", ""),
        ):
            with self.assertRaises(api_module.HTTPException) as context:
                require_write_key(None)

        self.assertEqual(context.exception.status_code, 503)

    def test_hardware_mode_rejects_missing_client_key(self) -> None:
        with (
            patch.object(api_module, "SERIAL_ENABLED", True),
            patch.object(api_module, "API_TOKEN", "secret-token"),
        ):
            with self.assertRaises(api_module.HTTPException) as context:
                require_write_key(None)

        self.assertEqual(context.exception.status_code, 401)

    def test_hardware_mode_accepts_matching_client_key(self) -> None:
        with (
            patch.object(api_module, "SERIAL_ENABLED", True),
            patch.object(api_module, "API_TOKEN", "secret-token"),
        ):
            require_write_key("secret-token")


class FakeSerial:
    def __init__(self, ack_line: bytes) -> None:
        self.ack_line = ack_line
        self.is_open = True
        self.written = b""

    def write(self, payload: bytes) -> None:
        self.written += payload

    def flush(self) -> None:
        pass

    def readline(self) -> bytes:
        return self.ack_line

    def close(self) -> None:
        self.is_open = False


class SerialAckTests(unittest.TestCase):
    def send_with_ack(self, ack_line: bytes) -> tuple[dict, FakeSerial]:
        controller = SerialController()
        connection = FakeSerial(ack_line)
        controller._connection = connection

        with patch.object(api_module, "SERIAL_ENABLED", True):
            result = controller.send_package(
                produto_id="PKG-001",
                categoria="smartphones",
                status="Válido",
            )

        return result, connection

    def test_accepts_matching_success_ack(self) -> None:
        result, connection = self.send_with_ack(
            b'{"ok":true,"produto_id":"PKG-001"}\n'
        )

        self.assertTrue(result["ok"])
        command = json.loads(connection.written.decode("utf-8"))
        self.assertEqual(command["produto_id"], "PKG-001")
        self.assertEqual(command["version"], 1)
        self.assertEqual(command["command"], "sort")

    def test_rejects_ack_timeout(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "ACK timeout"):
            self.send_with_ack(b"")

    def test_connect_uses_configured_ack_and_write_timeouts(self) -> None:
        controller = SerialController()
        connection = FakeSerial(b"")

        with (
            patch.object(api_module, "SERIAL_ENABLED", True),
            patch.object(api_module, "SERIAL_ACK_TIMEOUT_SECONDS", 5.0),
            patch.object(api_module, "SERIAL_WRITE_TIMEOUT_SECONDS", 1.0),
            patch.object(api_module.serial, "Serial", return_value=connection) as serial_ctor,
        ):
            self.assertTrue(controller.connect())

        serial_ctor.assert_called_once_with(
            api_module.ARDUINO_PORT,
            api_module.BAUD_RATE,
            timeout=5.0,
            write_timeout=1.0,
        )

    def test_rejects_non_json_ack(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "ACK JSON"):
            self.send_with_ack(b"OK\n")

    def test_rejects_negative_ack(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "rejected command"):
            self.send_with_ack(
                b'{"ok":false,"produto_id":"PKG-001","error":"invalid_command"}\n'
            )

    def test_rejects_ack_for_different_product(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "does not match"):
            self.send_with_ack(
                b'{"ok":true,"produto_id":"PKG-OTHER"}\n'
            )

    def test_rejects_ack_without_explicit_success(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "rejected command"):
            self.send_with_ack(b'{"produto_id":"PKG-001"}\n')


if __name__ == "__main__":
    unittest.main()
