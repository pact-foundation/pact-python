"""
Example test to show usage of matchers (and generators by extension).
"""

from __future__ import annotations

import logging
import re
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from random import randint, uniform
from threading import Thread
from typing import TYPE_CHECKING

import requests
from flask import Flask, Response, make_response
from yarl import URL

import pact._util
from pact import Pact, Verifier, generate, match

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@contextmanager
def start_provider() -> Generator[URL, None, None]:
    """
    Start the provider app using a daemon thread.

    Yields:
        The base URL of the running Flask server.
    """
    hostname = "127.0.0.1"
    port = pact._util.find_free_port()  # noqa: SLF001

    Thread(
        target=app.run,
        kwargs={"host": hostname, "port": port, "use_reloader": False},
        daemon=True,
    ).start()

    url = URL(f"http://{hostname}:{port}")

    for _ in range(50):
        try:
            response = requests.get(str(url / "_test" / "ping"), timeout=1)
            assert response.text == "pong"
            break
        except (requests.RequestException, AssertionError):
            time.sleep(0.1)
    else:
        msg = "Failed to ping provider"
        raise RuntimeError(msg)

    yield url


app = Flask(__name__)


@app.route("/path/to/<int:test_id>")
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


if __name__ == "__main__":
    app.run()


def test_matchers() -> None:
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("consumer", "provider").with_specification("V4")
    (
        pact
        .upon_receiving("a request")
        .given("a state", {"providerStateArgument": "providerStateValue"})
        .with_request("GET", match.regex("/path/to/100", regex=r"/path/to/\d{1,4}"))
        .with_query_parameter(
            "asOf",
            match.like(
                [match.date("2024-01-01", format="%Y-%m-%d")],
                min=1,
                max=1,
            ),
        )
        .will_respond_with(200)
        .with_body({
            "response": match.like(
                {
                    "regexMatches": match.regex(
                        "must end with 'hello world'",
                        regex=r"^.*hello world'$",
                    ),
                    "randomRegexMatches": match.regex(
                        regex=r"1-8 digits: \d{1,8}, 1-8 random letters \w{1,8}"
                    ),
                    "integerMatches": match.int(42),
                    "decimalMatches": match.decimal(3.1415),
                    "randomIntegerMatches": match.int(min=1, max=100),
                    "randomDecimalMatches": match.decimal(precision=4),
                    "booleanMatches": match.bool(False),
                    "randomStringMatches": match.string(size=10),
                    "includeMatches": match.includes("world"),
                    "includeWithGeneratorMatches": match.includes(
                        "world",
                        generator=generate.regex(r"\d{1,8} (hello )?world \d+"),
                    ),
                    "minMaxArrayMatches": match.each_like(
                        match.number(1.23, precision=2),
                        min=3,
                        max=5,
                    ),
                    "arrayContainingMatches": match.array_containing([
                        match.int(1),
                        match.int(2),
                    ]),
                    "numbers": {
                        "intMatches": match.number(42),
                        "floatMatches": match.number(3.1415),
                        "intGeneratorMatches": match.number(2, max=10),
                        "decimalGeneratorMatches": match.number(3.1415, precision=4),
                    },
                    "dateMatches": match.date("2024-01-01", format="%Y-%m-%d"),
                    "randomDateMatches": match.date(format="%Y-%m-%d"),
                    "timeMatches": match.time("12:34:56", format="%H:%M:%S"),
                    "timestampMatches": match.timestamp(
                        "2024-01-01T12:34:56.000000",
                        format="%Y-%m-%dT%H:%M:%S.%f",
                    ),
                    "nullMatches": match.null(),
                    "eachKeyMatches": match.each_key_matches(
                        {
                            "id_1": match.each_value_matches(
                                {"name": match.string(size=30)},
                                rules=match.string("John Doe"),
                            )
                        },
                        rules=match.regex("id_1", regex=r"^id_\d+$"),
                    ),
                },
                min=1,
            )
        })
        .with_header(
            "SpecialHeader", match.regex("Special: Foo", regex=r"^Special: \w+$")
        )
    )
    with pact.serve() as mockserver:
        response = requests.get(
            f"{mockserver.url}/path/to/35?asOf=2020-05-13", timeout=5
        )
        response_data = response.json()
        # when a value is passed to a matcher, that value should be returned
        assert (
            response_data["response"]["regexMatches"] == "must end with 'hello world'"
        )
        assert response_data["response"]["integerMatches"] == 42
        assert response_data["response"]["booleanMatches"] is False
        assert response_data["response"]["includeMatches"] == "world"
        assert response_data["response"]["dateMatches"] == "2024-01-01"
        assert response_data["response"]["timeMatches"] == "12:34:56"
        assert (
            response_data["response"]["timestampMatches"]
            == "2024-01-01T12:34:56.000000"
        )
        assert response_data["response"]["arrayContainingMatches"] == [1, 2]
        assert response_data["response"]["nullMatches"] is None
        # when a value is not passed to a matcher, a value should be generated
        random_regex_matcher = re.compile(
            r"1-8 digits: \d{1,8}, 1-8 random letters \w{1,8}"
        )
        assert random_regex_matcher.match(
            response_data["response"]["randomRegexMatches"]
        )
        random_integer = int(response_data["response"]["randomIntegerMatches"])
        assert random_integer >= 1
        assert random_integer <= 100
        float(response_data["response"]["randomDecimalMatches"])
        assert (
            len(response_data["response"]["randomDecimalMatches"].replace(".", "")) == 4
        )
        assert len(response_data["response"]["randomStringMatches"]) == 10

    pact.write_file(pact_dir, overwrite=True)
    with start_provider() as url:
        verifier = (
            Verifier("My Provider", host="127.0.0.1")
            .add_transport(url=url)
            .add_source(pact_dir / "consumer-provider.json")
        )
        verifier.verify()
