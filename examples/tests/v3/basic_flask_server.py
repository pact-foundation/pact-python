"""
Simple flask server for matcher example.
"""

import logging
import re
import signal
import subprocess
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from random import randint, uniform
from threading import Thread
from typing import NoReturn

import requests
from yarl import URL

from flask import Flask, Response, make_response

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
        random_regex_matches = "1-8 digits: 12345678, 1-8 random letters abcdefgh"
        response = make_response({
            "response": {
                "id": test_id,
                "regexMatches": "must end with 'hello world'",
                "randomRegexMatches": random_regex_matches,
                "integerMatches": test_id,
                "decimalMatches": round(uniform(0, 9), 3),  # noqa: S311
                "booleanMatches": True,
                "randomIntegerMatches": randint(1, 100),  # noqa: S311
                "randomDecimalMatches": round(uniform(0, 9), 1),  # noqa: S311
                "randomStringMatches": "hi there",
                "includeMatches": "hello world",
                "includeWithGeneratorMatches": "say 'hello world' for me",
                "minMaxArrayMatches": [
                    round(uniform(0, 9), 1)  # noqa: S311
                    for _ in range(randint(3, 5))  # noqa: S311
                ],
                "arrayContainingMatches": [randint(1, 100), randint(1, 100)],  # noqa: S311
                "numbers": {
                    "intMatches": 42,
                    "floatMatches": 3.1415,
                    "intGeneratorMatches": randint(1, 100),  # noqa: S311,
                    "decimalGeneratorMatches": round(uniform(10, 99), 2),  # noqa: S311
                },
                "dateMatches": "1999-12-31",
                "randomDateMatches": "1999-12-31",
                "timeMatches": "12:34:56",
                "timestampMatches": datetime.now().isoformat(),  # noqa: DTZ005
                "nullMatches": None,
                "eachKeyMatches": {
                    "id_1": {
                        "name": "John Doe",
                    },
                    "id_2": {
                        "name": "Jane Doe",
                    },
                },
            }
        })
        response.headers["SpecialHeader"] = "Special: Hi"
        return response

    @app.get("/_test/ping")
    def ping() -> str:
        """Simple ping endpoint for testing."""
        return "pong"

    app.run()
