
def pytest_addoption(parser):
    parser.addoption(
        "--publish-pact", type=str, action="store",
        help="Upload generated pact file to pact broker with version"
    )
