"""
Example test to show usage of matchers (and generators by extension).
"""

import re
from pathlib import Path

import requests

from examples.tests.v3.basic_flask_server import start_provider
from pact.v3 import Pact, Verifier, generators, matchers


def test_matchers() -> None:
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("consumer", "provider").with_specification("V4")
    (
        pact.upon_receiving("a request")
        .given("a state", parameters={"providerStateArgument": "providerStateValue"})
        .with_request("GET", matchers.regex(r"/path/to/\d{1,4}", "/path/to/100"))
        .with_query_parameter(
            "asOf",
            matchers.like(
                [
                    matchers.date("yyyy-MM-dd", "2024-01-01"),
                ],
                min_count=1,
                max_count=1,
            ),
        )
        .will_respond_with(200)
        .with_body({
            "response": matchers.like(
                {
                    "regexMatches": matchers.regex(
                        r".*hello world'$", "must end with 'hello world'"
                    ),
                    "randomRegexMatches": matchers.regex(
                        r"1-8 digits: \d{1,8}, 1-8 random letters \w{1,8}"
                    ),
                    "integerMatches": matchers.integer(42),
                    "decimalMatches": matchers.decimal(3.1415),
                    "randomIntegerMatches": matchers.integer(min_val=1, max_val=100),
                    "randomDecimalMatches": matchers.decimal(digits=4),
                    "booleanMatches": matchers.boolean(value=False),
                    "randomStringMatches": matchers.string(size=10),
                    "includeMatches": matchers.includes("world"),
                    "includeWithGeneratorMatches": matchers.includes(
                        "world", generators.regex(r"\d{1,8} (hello )?world \d+")
                    ),
                    "minMaxArrayMatches": matchers.each_like(
                        matchers.number(digits=2),
                        min_count=3,
                        max_count=5,
                    ),
                    "arrayContainingMatches": matchers.array_containing([
                        matchers.integer(1),
                        matchers.integer(2),
                    ]),
                    "dateMatches": matchers.date("yyyy-MM-dd", "2024-01-01"),
                    "randomDateMatches": matchers.date("yyyy-MM-dd"),
                    "timeMatches": matchers.time("HH:mm:ss", "12:34:56"),
                    "timestampMatches": matchers.timestamp(
                        "yyyy-MM-dd'T'HH:mm:ss.SSSSSS", "2024-01-01T12:34:56.000000"
                    ),
                    "nullMatches": matchers.null(),
                    "eachKeyMatches": matchers.each_key_matches(
                        {
                            "id_1": matchers.each_value_matches(
                                {
                                    "name": matchers.string(size=30),
                                },
                                rules=matchers.string("John Doe"),
                            )
                        },
                        rules=matchers.regex(r"id_\d+", "id_1"),
                    ),
                },
                min_count=1,
            )
        })
        .with_header("SpecialHeader", matchers.regex(r"Special: \w+", "Special: Foo"))
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
        assert response_data["response"]["integerMatches"] == 42  # noqa: PLR2004
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
        assert random_integer <= 100  # noqa: PLR2004
        float(response_data["response"]["randomDecimalMatches"])
        assert (
            len(response_data["response"]["randomDecimalMatches"].replace(".", "")) == 4  # noqa: PLR2004
        )
        assert len(response_data["response"]["randomStringMatches"]) == 10  # noqa: PLR2004

    pact.write_file(pact_dir, overwrite=True)
    with start_provider() as url:
        verifier = (
            Verifier()
            .set_info("My Provider", url=url)
            .add_source(pact_dir / "consumer-provider.json")
        )
        verifier.verify()
