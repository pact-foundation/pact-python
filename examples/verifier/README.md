# Introduction

This is an e2e example to show the provider verification working.

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
pytest tests/test_user_consumer.py::test_get_non_existing_user
```
