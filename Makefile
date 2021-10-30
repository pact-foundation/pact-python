DOCS_DIR := ./docs


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
examples: consumer flask fastapi messaging


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
