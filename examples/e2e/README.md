# Introduction

This is an e2e example using flask to help as a guide to getting started with Pact for Python. For the provider it imports the app into a wrapper (pact_provider.py) so as to decorate extra functions we can use to test our app.

## Setup

Create your own virtualenv for this. Run

```bash
pip install -r requirements.txt
pip install pact-python
```

TODO: Make this so you can point to the parent install to help with development.

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
pytest tests/test_user_consumer.py::test_get_non_existing_user
```

If you want to publish this to the pact broker add the '--publish-pact' option like:

```bash
pytest  --publish-pact=XX
```

XX is the version number of the pact and is for you to manage in your deployment process.

Sometimes you may get the mock server in a hung state. You can kill it via (untested):

```bash
pkill -f pact-mock-service.rb
```

## Provider States

Run the script (placeholder version number for pact broker)

```bash
./verify_pact.sh 1
```

This will import the provider.py file which is the actual app and then decorate it with extra urls. It then puts this into the background and runs the pact-verifier tool against it.

To test what this looks like when failing change one of these values.

```python
def setup_user_a_nonadmin():

    id = '00000000-0000-4000-a000-000000000000'
    some_date = '2016-12-15T20:16:01'

```

### Provider debugging

To manually trigger one of the 2 manual states you can run:

```bash
curl -X POST -H "Content-Type: application/json"  --data "{\"state\": \"UserA exists and is not an administrator\"}" http://127.0.0.1:5000/_pact/provider_states
```

Changing the json content to match the state you want.
