from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests

DEMO_PACKAGES = [
    {
        "produto_id": "DEMO-HTTP-001",
        "categoria": "smartphones",
        "descricao": "Smartphone demo via API",
        "peso": 0.45,
        "altura": 15.0,
    },
    {
        "produto_id": "DEMO-HTTP-002",
        "categoria": "tablets",
        "descricao": "Tablet demo via API",
        "peso": 0.72,
        "altura": 24.0,
    },
    {
        "produto_id": "DEMO-HTTP-003",
        "categoria": "livros",
        "descricao": "Categoria inválida para demonstrar rejeição",
        "peso": 0.30,
        "altura": 21.0,
    },
]


def request_json(
    method: str,
    url: str,
    *,
    timeout: float,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    response = requests.request(
        method,
        url,
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def get_counter(base_url: str, endpoint: str, key: str, timeout: float) -> int:
    payload = request_json("GET", f"{base_url}{endpoint}", timeout=timeout)
    return int(payload[key])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a safe end-to-end software demo against the FastAPI service."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the running API.",
    )
    parser.add_argument(
        "--api-token",
        default=os.getenv("API_TOKEN", ""),
        help="Optional API token. Defaults to API_TOKEN from the environment.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--allow-hardware",
        action="store_true",
        help="Allow the demo to POST packages when hardware mode is enabled.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Exit non-zero if expected counter/status changes are not observed.",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    headers = {"X-API-Key": args.api_token} if args.api_token else {}

    try:
        health = request_json(
            "GET",
            f"{base_url}/api/health",
            timeout=args.timeout,
        )
    except requests.RequestException as exc:
        print(f"API unavailable: {exc}", file=sys.stderr)
        return 2

    if health.get("serial_enabled") and not args.allow_hardware:
        print(
            "Refusing to run demo: hardware mode is enabled. "
            "Use SERIAL_ENABLED=false or pass --allow-hardware explicitly.",
            file=sys.stderr,
        )
        return 3

    before = {
        "total": get_counter(base_url, "/api/total_itens", "total_itens", args.timeout),
        "valid": get_counter(base_url, "/api/total_validos", "total_validos", args.timeout),
        "invalid": get_counter(
            base_url,
            "/api/total_invalidos",
            "total_invalidos",
            args.timeout,
        ),
    }

    expected_statuses = ["Válido", "Válido", "Inválido"]
    responses: list[dict[str, Any]] = []

    try:
        for package in DEMO_PACKAGES:
            response = request_json(
                "POST",
                f"{base_url}/produto",
                timeout=args.timeout,
                headers=headers,
                payload=package,
            )
            responses.append(response)
    except requests.RequestException as exc:
        print(f"Demo request failed: {exc}", file=sys.stderr)
        return 4

    after = {
        "total": get_counter(base_url, "/api/total_itens", "total_itens", args.timeout),
        "valid": get_counter(base_url, "/api/total_validos", "total_validos", args.timeout),
        "invalid": get_counter(
            base_url,
            "/api/total_invalidos",
            "total_invalidos",
            args.timeout,
        ),
    }

    recent = request_json(
        "GET",
        f"{base_url}/api/ultimos_produtos",
        timeout=args.timeout,
    )

    report = {
        "health": health,
        "before": before,
        "responses": responses,
        "after": after,
        "recent_count": len(recent),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not args.verify:
        return 0

    actual_statuses = [response.get("status") for response in responses]
    expected_after = {
        "total": before["total"] + 3,
        "valid": before["valid"] + 2,
        "invalid": before["invalid"] + 1,
    }

    problems: list[str] = []

    if actual_statuses != expected_statuses:
        problems.append(
            f"unexpected statuses: expected {expected_statuses}, got {actual_statuses}"
        )

    for key, expected_value in expected_after.items():
        if after[key] != expected_value:
            problems.append(
                f"{key} counter mismatch: expected {expected_value}, got {after[key]}"
            )

    if not health.get("serial_enabled"):
        for response in responses:
            serial_data = response.get("serial") or {}
            if serial_data.get("mode") != "simulation":
                problems.append("simulation response did not report mode=simulation")
                break

    if problems:
        for problem in problems:
            print(f"VERIFY FAILED: {problem}", file=sys.stderr)
        return 5

    print("VERIFY PASSED: API demo produced the expected state transitions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
