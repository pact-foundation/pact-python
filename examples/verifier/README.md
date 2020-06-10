# Introduction

This is a verifier example.

## Setup

Create your own virtualenv for this. Run

```bash
pip install -r requirements.txt
```

This should provide you with a relative path to pact install relatively (2 dirs up)

Create the local broker (for demo purposes only) To do this separately clone this repo:
* https://github.com/pact-foundation/pact-broker-docker

Then from where this is install run in it's own terminal

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
pytest tests/xxx.py::test_yyy
```
