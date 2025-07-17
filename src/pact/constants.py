"""
Constant values for the pact-python package.

The constants in this module are simply re-exported from the `pact_cli` module.
"""

import pact_cli

BROKER_CLIENT_PATH = pact_cli.BROKER_CLIENT_PATH or ""
MESSAGE_PATH = pact_cli.MESSAGE_PATH or ""
MOCK_SERVICE_PATH = pact_cli.MOCK_SERVICE_PATH or ""
VERIFIER_PATH = pact_cli.VERIFIER_PATH or ""
