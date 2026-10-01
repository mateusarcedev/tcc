import os
import unittest

os.environ["SERIAL_ENABLED"] = "false"
os.environ["DATABASE_PATH"] = ":memory:"

from api.api import package_status  # noqa: E402


class PackageStatusTests(unittest.TestCase):
    def test_smartphones_are_valid(self) -> None:
        self.assertEqual(package_status("smartphones"), "Válido")

    def test_tablets_are_valid_case_insensitively(self) -> None:
        self.assertEqual(package_status("  TABLETS  "), "Válido")

    def test_other_categories_are_invalid(self) -> None:
        self.assertEqual(package_status("livros"), "Inválido")


if __name__ == "__main__":
    unittest.main()
