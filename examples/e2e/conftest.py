
from testcontainers.compose import DockerCompose

import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--publish-pact", type=str, action="store",
        help="Upload generated pact file to pact broker with version"
    )

    parser.addoption(
        "--provider-url", type=str, action="store",
        help="The url to our provider."
    )

    parser.addoption(
        "--run-broker", type=bool, action="store",
        help="Whether to run broker in this test or not."
    )

# This fixture is to simulate a managed Pact Broker or Pactflow account
# Do not do this yourself but setup one of the above
# https://github.com/pact-foundation/pact_broker
@pytest.fixture(scope='session', autouse=True)
def broker(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    # yield
    if not publish:
        yield
        return

    run_broker = request.config.getoption('--run-broker')

    if not run_broker:
        yield
        return
    else:
        print('Starting broker')
        with DockerCompose("../broker",
                           compose_file_name=["docker-compose.yml"],
                           pull=True) as compose:

            stdout, stderr = compose.get_logs()
            if stderr:
                print("Errors\\n:{}".format(stderr))
            print(stdout)
            yield
