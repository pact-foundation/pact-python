from pathlib import Path

from examples.tests.v3.basic_flask_server import start_provider
from pact.v3 import Pact, Verifier, matchers


def test_matchers() -> None:
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("consumer", "provider").with_specification("V4")
    (
        pact.upon_receiving("a request")
        .given("a state")
        .with_request(
            "GET",
            matchers.regex("/path/to/100", r"/path/to/\d+", generator="Regex")
        )
        .will_respond_with(200)
        .with_body(
            {
                "response": matchers.like(
                    {
                        "regex": matchers.regex(
                            "must end with 'hello world'", r".*hello world'$"
                        ),
                        "integer": matchers.integer(42),
                        "include": matchers.include("hello world", "world"),
                        "minMaxArray": matchers.each_like(
                            matchers.decimal(1.0),
                            min_count=3,
                            max_count=5,
                        ),
                    },
                    min_count=1,
                )
            }
        )
        .with_header(
            "SpecialHeader", matchers.regex("Special: Foo", r"Special: \w+")
        )
    )
    pact.write_file(pact_dir, overwrite=True)
    with start_provider() as url:
        verifier = (
            Verifier()
            .set_info("My Provider", url=url)
            .add_source(pact_dir / "consumer-provider.json")
        )
        verifier.verify()
