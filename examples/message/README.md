# Introduction

This is an e2e example that uses messages, including a sample implementation of a message handler.

## Setup

Create your own virtualenv for this. Run

```bash
pip install -r requirements.txt
pip install ../../
pytest
```

This should provide you with a relative path to pact install relatively (2 dirs up)

Create the local broker (for demo purposes only) Open a separate terminal in the examples/broker folder and run:
```bash
docker-compose up
```

If you can open a browser to http://localhost and see the broker you have succeeded.
If needed, log-in using the provided details in tests such as:

```
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
```

## Message Consumer

From the root directory run:

```bash
pytest
```

Or you can run individual tests like:

```bash
pytest tests/consumer/test_message_consumer.py::test_generate_pact_file
```
