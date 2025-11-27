"""Utility script to spin up the FastAPI service briefly and verify key endpoints."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the FastAPI service")
    parser.add_argument("--host", default=HOST, help="Host to bind and hit (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=PORT, help="Port to bind and hit (default: 8000)")
    parser.add_argument("--equipment-id", default="MRI-01", help="ID to send in the payload")
    parser.add_argument("--temperature", type=float, default=72.1, help="Temperature reading")
    parser.add_argument("--pressure", type=float, default=2.1, help="Pressure reading")
    parser.add_argument("--vibration", type=float, default=0.05, help="Vibration reading")
    return parser.parse_args()


def wait_for_server(host: str, port: int, timeout: float = 30.0, interval: float = 0.5) -> dict:
    """Poll the /health endpoint until it responds or timeout expires."""
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=5) as response:
                return json.load(response)
        except Exception as exc:  # noqa: BLE001 - best effort polling
            last_error = exc
            time.sleep(interval)

    raise TimeoutError(f"Service did not become ready within {timeout}s") from last_error


def call_predict(host: str, port: int, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=f"http://{host}:{port}/predict",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def stream_server_logs(pipe) -> None:
    if not pipe:
        return
    for line in pipe:
        print(line.rstrip())


def main() -> None:
    args = parse_args()
    payload = {
        "equipment_id": args.equipment_id,
        "temperature": args.temperature,
        "pressure": args.pressure,
        "vibration": args.vibration,
    }

    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]

    print("Starting FastAPI service...", flush=True)
    server = subprocess.Popen(
        uvicorn_cmd,
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        health = wait_for_server(args.host, args.port)
        print("/health response:")
        print(json.dumps(health, indent=2))

        prediction = call_predict(args.host, args.port, payload)
        print("/predict response:")
        print(json.dumps(prediction, indent=2))
    finally:
        print("Stopping FastAPI service...", flush=True)
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        print("--- Server output ---")
        stream_server_logs(server.stdout)


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:  # surface nicer error if port already in use
        raise SystemExit(f"Failed to reach service: {exc}") from exc
