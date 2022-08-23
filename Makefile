DOCS_DIR := ./docs

PROJECT := pact-python
PYTHON_MAJOR_VERSION := 3.9

sgr0 := $(shell tput sgr0)
red := $(shell tput setaf 1)
green := $(shell tput setaf 2)

help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  deps       to install the required files for development"
	@echo "  verifier   to run the verifier end to end tests"
	@echo "  examples   to run the example end to end tests (consumer, fastapi, flask, messaging)"
	@echo "  consumer   to run the example consumer tests"
	@echo "  fastapi    to run the example FastApi provider tests"
	@echo "  flask      to run the example Flask provider tests"
	@echo "  messaging  to run the example messaging e2e tests"
	@echo "  package    to create a distribution package in /dist/"
	@echo "  release    to perform a release build, including deps, test, and package targets"
	@echo "  test       to run all tests"
	@echo "  venv       to setup a venv under .venv using pyenv, if available"
	@echo ""


.PHONY: release
release: deps test package


.PHONY: clean
clean:
	rm -rf build
	rm -rf dist
	rm -rf pact/bin


.PHONY: deps
deps:
	pip install -r requirements_dev.txt -e .


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
examples: messaging


.PHONY: package
package:
	python setup.py sdist


.PHONY: test
test: deps
	flake8
	pydocstyle pact
	coverage erase
	tox
	coverage report -m --fail-under=100

.PHONY: venv
venv:
	@if [ -d "./.venv" ]; then echo "$(red).venv already exists, not continuing!$(sgr0)"; exit 1; fi
	@type pyenv >/dev/null 2>&1 || (echo "$(red)pyenv not found$(sgr0)"; exit 1)

	@echo "\n$(green)Try to find the most recent minor version of the major version specified$(sgr0)"
	$(eval PYENV_VERSION=$(shell pyenv install -l | grep "\s\s$(PYTHON_MAJOR_VERSION)\.*" | tail -1 | xargs))
	@echo "$(PYTHON_MAJOR_VERSION) -> $(PYENV_VERSION)"

	@echo "\n$(green)Install the Python pyenv version if not already available$(sgr0)"
	pyenv install $(PYENV_VERSION) -s

	@echo "\n$(green)Make a .venv dir$(sgr0)"
	~/.pyenv/versions/${PYENV_VERSION}/bin/python3 -m venv ${CURDIR}/.venv

	@echo "\n$(green)Make it 'available' to pyenv$(sgr0)"
	ln -sf ${CURDIR}/.venv ~/.pyenv/versions/${PROJECT}

	@echo "\n$(green)Use it! (populate .python-version)$(sgr0)"
	pyenv local ${PROJECT}
