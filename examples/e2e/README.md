# Introduction

This is an e2e example to show the provider verification working for both CLI and Python API. 

Note: in this example within conftest we are creating a Broker instance. This is purely to help demonstrate using Pact Broker in the code and you are
strongly advised to set up a persistent Broker or use Pactflow

## Setup

Create your own virtualenv for this. Run

```bash
pip install -r requirements.txt
pip install -e ../../
./run_pytest.sh
```

This should provide you with a relative path to pact install relatively (2 dirs up) You can look at the Makefile in the root folder for more details.


# Running
This example runs broker as part of it's tests. However, if you did wish to create the local broker open a separate terminal in the examples/broker folder and run:
```bash
docker-compose up
```

If you can open a browser to http://localhost and see the broker you have succeeded. You will have to remove the fixture in conftest.py to get this for the consumer to work, however.

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

This example is using the python verifier code. There is an example script of how you could run the verifier cli which would be invoked like:
```bash
./verify_pact.sh 2
```