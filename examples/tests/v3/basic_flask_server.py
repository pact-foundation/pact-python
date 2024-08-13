import logging
import re
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from typing import Generator, NoReturn

import requests
from flask import Flask, Response, make_response
from yarl import URL

logger = logging.getLogger(__name__)

@contextmanager
def start_provider() -> Generator[URL, None, None]:  # noqa: C901
    """
    Start the provider app.
    """
    process = subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            Path(__file__),
        ],
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    pattern = re.compile(r" \* Running on (?P<url>[^ ]+)")
    while True:
        if process.poll() is not None:
            logger.error("Provider process exited with code %d", process.returncode)
            logger.error(
                "Provider stdout: %s", process.stdout.read() if process.stdout else ""
            )
            logger.error(
                "Provider stderr: %s", process.stderr.read() if process.stderr else ""
            )
            msg = f"Provider process exited with code {process.returncode}"
            raise RuntimeError(msg)
        if (
            process.stderr
            and (line := process.stderr.readline())
            and (match := pattern.match(line))
        ):
            break
        time.sleep(0.1)

    url = URL(match.group("url"))
    logger.debug("Provider started on %s", url)
    for _ in range(50):
        try:
            response = requests.get(str(url / "_test" / "ping"), timeout=1)
            assert response.text == "pong"
            break
        except (requests.RequestException, AssertionError):
            time.sleep(0.1)
            continue
    else:
        msg = "Failed to ping provider"
        raise RuntimeError(msg)

    def redirect() -> NoReturn:
        while True:
            if process.stdout:
                while line := process.stdout.readline():
                    logger.debug("Provider stdout: %s", line.strip())
            if process.stderr:
                while line := process.stderr.readline():
                    logger.debug("Provider stderr: %s", line.strip())

    thread = Thread(target=redirect, daemon=True)
    thread.start()

    try:
        yield url
    finally:
        process.send_signal(signal.SIGINT)

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/path/to/<test_id>")
    def hello_world(test_id: int) -> Response:
        response = make_response(
            {
                "response": {
                    "id": test_id,
                    "regex": "must end with 'hello world'",
                    "integer": 42,
                    "include": "hello world",
                    "minMaxArray": [1.0, 1.1, 1.2],
                }
            }
        )
        response.headers["SpecialHeader"] = "Special: Hi"
        return response

    @app.get("/_test/ping")
    def ping() -> str:
        """Simple ping endpoint for testing."""
        return "pong"

    app.run()
