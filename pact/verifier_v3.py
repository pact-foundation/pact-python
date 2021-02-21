"""Classes and methods to verify Contracts (V3 implementation)."""

from pact_python_v3 import verify_provider


class VerifierV3(object):
    """A Pact V3 Verifier."""

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
        return 'V3 Verifier for {} with url {}'.format(self.provider, self.provider_base_url)

    def verify_pacts(self, **kwargs):
        """Verify the pacts against the provider.

        Args:
            sources ([string]): Pact sources
            pactBrokerUrl?: string
            providerStatesSetupUrl?: string
            pactBrokerUsername?: string
            pactBrokerPassword?: string
            pactBrokerToken?: string

            callbackTimeout?: number
            publishVerificationResult?: boolean
            providerVersion?: string
            requestFilter?: (req: any) => any
            stateHandlers?: any

            consumerVersionTags?: string | string[]
            providerVersionTags?: string | string[]
            // consumerVersionSelectors?: ConsumerVersionSelector[];
            enablePending?: boolean
            includeWipPactsSince?: string
            disableSSLVerification?: boolean

        Returns:
          success: True if no failures

        """

        print(kwargs)
        return verify_provider(self.provider, self.provider_base_url, kwargs)
