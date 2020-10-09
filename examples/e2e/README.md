# Introduction

This is an e2e example to show the provider verification working for both cli and python api.

## Setup

Create your own virtualenv for this. Run

```bash
pip install -r requirements.txt
pip install ../../
```

 pip install pipenv
$ pipenv install
pipenv shell
pytest

This should provide you with a relative path to pact install relatively (2 dirs up)

Create the local broker (for demo purposes only) Open a separate terminal in the examples/broker folder and run:
```bash
docker-compose up
```

If you can open a browser to http://localhost and see the broker you have succeeded.

## Consumer

From the root directory run:

```bash
pytest
```

Or you can run individual tests like:

```bash
pytest tests/consumer/test_user_consumer.py::test_get_non_existing_user
```

To get the consumer to publish a pact to broker you will need to run (2 is an arbitary version number):
```bash
pytest tests/consumer/test_user_consumer.py --publish-pact 2
```

And then you can run:
```bash
./verify_pact.sh 2
```

To verify the pact
