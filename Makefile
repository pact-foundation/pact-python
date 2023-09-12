DOCS_DIR := ./docs

PROJECT := pact-python
PYTHON_MAJOR_VERSION := 3.11

sgr0 := $(shell tput sgr0)
red := $(shell tput setaf 1)
green := $(shell tput setaf 2)

help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  examples   to run the example end to end tests (consumer, fastapi, flask, messaging)"
	@echo "  consumer   to run the example consumer tests"
	@echo "  fastapi    to run the example FastApi provider tests"
	@echo "  flask      to run the example Flask provider tests"
	@echo "  messaging  to run the example messaging e2e tests"
	@echo "  package    to create a distribution package in /dist/"
	@echo "  release    to perform a release build, including deps, test, and package targets"
	@echo "  test       to run all tests"
	@echo ""


.PHONY: release
release: test package


.PHONY: clean
clean:
	hatch clean


define CONSUMER
	echo "consumer make"
	cd examples/consumer
	pip install -q -r requirements.txt
	pip install -e ../../
	./run_pytest.sh
endef
export CONSUMER


define FLASK_PROVIDER
	echo "flask make"
	cd examples/flask_provider
	pip install -q -r requirements.txt
	pip install -e ../../
	./run_pytest.sh
endef
export FLASK_PROVIDER


define FASTAPI_PROVIDER
	echo "fastapi make"
	cd examples/fastapi_provider
	pip install -q -r requirements.txt
	pip install -e ../../
	./run_pytest.sh
endef
export FASTAPI_PROVIDER


define MESSAGING
	echo "messaging make"
	cd examples/message
	pip install -q -r requirements.txt
	pip install -e ../../
	./run_pytest.sh
endef
export MESSAGING


.PHONY: consumer
consumer:
	bash -c "$$CONSUMER"


.PHONY: flask
flask:
	bash -c "$$FLASK_PROVIDER"


.PHONY: fastapi
fastapi:
	bash -c "$$FASTAPI_PROVIDER"


.PHONY: messaging
messaging:
	bash -c "$$MESSAGING"


.PHONY: examples
examples: consumer flask fastapi messaging


.PHONY: package
package:
	hatch build


.PHONY: test
test:
	hatch run all
	hatch run test:all
	coverage report -m --fail-under=100
