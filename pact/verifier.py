"""Classes and methods to verify Contracts."""
from pact.verify_wrapper import VerifyWrapper, path_exists, sanitize_logs, expand_directories

class Verifier(object):
    """A Pact Verifier."""

    def __init__(self, provider, provider_base_url, **kwargs):
        """Create a new Verifier.

        Args:
            provider ([String]): provider name
            provider_base_url ([String]): provider url

        """
        self.provider = provider
        self.provider_base_url = provider_base_url

    def __str__(self):
        """Return string representation.

        Returns:
            [String]: verifier description.

        """
        return 'Verifier for {} with url {}'.format(self.provider, self.provider_base_url)

    def validate_publish(self, **kwargs):
        """Validate publish has a version."""
        if ((kwargs.get('publish') is not None) and (kwargs.get('publish_version') is None)):
            # do something
            raise Exception()

    def verify_pacts(self, *pacts, **kwargs):
        """Verify our pacts from the provider.

        Returns:
          success: True if no failures
          logs: some tbd output of logs

        """
        self.validate_publish(**kwargs)
        verbose = kwargs.get('verbose', False)

        missing_files = [path for path in pacts if not path_exists(path)]
        if missing_files:
            raise Exception("Missing pact files {}".format(missing_files))

        pacts = expand_directories(pacts)

        # rerun_command()  # env =

        success, logs = VerifyWrapper().call_verify(*pacts,
                                                    provider=self.provider,
                                                    provider_base_url=self.provider_base_url)

        sanitize_logs(logs, verbose)
        return success, logs

    def verify_with_broker(self, broker_username, broker_password, broker_url, **kwargs):
        """Use Broker to verify.

        Args:
            broker_username ([String]): broker username
            broker_password ([String]): broker password
            broker_url ([String]): url of broker

        """
        verbose = kwargs.get('verbose', False)

        success, logs = VerifyWrapper().call_verify(broker_username=broker_username,
                                                    broker_password=broker_password,
                                                    broker_url=broker_url,
                                                    provider=self.provider,
                                                    provider_base_url=self.provider_base_url)
        sanitize_logs(logs, verbose)

        return success, logs
