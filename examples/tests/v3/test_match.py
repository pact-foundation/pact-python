"""
Example test to show usage of matchers (and generators by extension).
"""

import re
from pathlib import Path

import requests

from examples.tests.v3.basic_flask_server import start_provider
from pact.v3 import Pact, Verifier, generate, match


def test_matchers() -> None:
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("consumer", "provider").with_specification("V4")
    (
        pact.upon_receiving("a request")
        .given("a state", parameters={"providerStateArgument": "providerStateValue"})
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
            Verifier()
            .set_info("My Provider", url=url)
            .add_source(pact_dir / "consumer-provider.json")
        )
        verifier.verify()
