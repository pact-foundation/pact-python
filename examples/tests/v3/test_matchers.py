"""
Example test to show usage of matchers (and generators by extension).
"""

import re
from pathlib import Path

import requests

from examples.tests.v3.basic_flask_server import start_provider
from pact.v3 import Pact, Verifier, generators, match


def test_matchers() -> None:
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("consumer", "provider").with_specification("V4")
    (
        pact.upon_receiving("a request")
        .given("a state", parameters={"providerStateArgument": "providerStateValue"})
        .with_request("GET", match.regex(r"/path/to/\d{1,4}", "/path/to/100"))
        .with_query_parameter(
            "asOf",
            match.like(
                [
                    match.date("yyyy-MM-dd", "2024-01-01"),
                ],
                min_count=1,
                max_count=1,
            ),
        )
        .will_respond_with(200)
        .with_body({
            "response": match.like(
                {
                    "regexMatches": match.regex(
                        r".*hello world'$", "must end with 'hello world'"
                    ),
                    "randomRegexMatches": match.regex(
                        r"1-8 digits: \d{1,8}, 1-8 random letters \w{1,8}"
                    ),
                    "integerMatches": match.integer(42),
                    "decimalMatches": match.decimal(3.1415),
                    "randomIntegerMatches": match.integer(min_val=1, max_val=100),
                    "randomDecimalMatches": match.decimal(digits=4),
                    "booleanMatches": match.boolean(value=False),
                    "randomStringMatches": match.string(size=10),
                    "includeMatches": match.includes("world"),
                    "includeWithGeneratorMatches": match.includes(
                        "world", generators.regex(r"\d{1,8} (hello )?world \d+")
                    ),
                    "minMaxArrayMatches": match.each_like(
                        match.number(digits=2),
                        min_count=3,
                        max_count=5,
                    ),
                    "arrayContainingMatches": match.array_containing([
                        match.integer(1),
                        match.integer(2),
                    ]),
                    "numbers": {
                        "intMatches": match.number(42),
                        "floatMatches": match.number(3.1415),
                        "intGeneratorMatches": match.number(max_val=10),
                        "decimalGeneratorMatches": match.number(digits=4),
                    },
                    "dateMatches": match.date("yyyy-MM-dd", "2024-01-01"),
                    "randomDateMatches": match.date("yyyy-MM-dd"),
                    "timeMatches": match.time("HH:mm:ss", "12:34:56"),
                    "timestampMatches": match.timestamp(
                        "yyyy-MM-dd'T'HH:mm:ss.SSSSSS", "2024-01-01T12:34:56.000000"
                    ),
                    "nullMatches": match.null(),
                    "eachKeyMatches": match.each_key_matches(
                        {
                            "id_1": match.each_value_matches(
                                {
                                    "name": match.string(size=30),
                                },
                                rules=match.string("John Doe"),
                            )
                        },
                        rules=match.regex(r"id_\d+", "id_1"),
                    ),
                },
                min_count=1,
            )
        })
        .with_header("SpecialHeader", match.regex(r"Special: \w+", "Special: Foo"))
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
        assert response_data["response"]["nullMatches"] == ""
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
