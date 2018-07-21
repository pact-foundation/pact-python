DOCS_DIR := ./docs


help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  deps       to install the required files for development"
	@echo "  e2e        to run the end to end tests"
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


define E2E
	set -ex
	cd e2e
	nosetests ./contracts
	python app.py &
	APP_PID=$$!
	function teardown {
		echo 'Tearing down Flask server'
		kill $$APP_PID
	}
	trap teardown EXIT
	while ! nc -z localhost 5000; do
		sleep 0.1
	done

	set +e
	pact-verifier \
		--provider-base-url=http://localhost:5000 \
		--provider-states-url=http://localhost:5000/_pact/provider-states \
		--provider-states-setup-url=http://localhost:5000/_pact/provider-states/active \
		./pacts/failing-consumer-provider.json
	EXIT_CODE=$$?
	set -e

	if [ $$EXIT_CODE -eq 1 ]; then
		echo "Failing verification exited with 1 as expected"
	else
		echo "Failing verification did not exit with 1 as expected"
		exit 1
	fi

	pact-verifier \
		--provider-base-url=http://localhost:5000 \
		--provider-states-url=http://localhost:5000/_pact/provider-states \
		--provider-states-setup-url=http://localhost:5000/_pact/provider-states/active \
		./pacts/consumer-provider.json

endef


export E2E
.PHONY: e2e
e2e:
	bash -c "$$E2E"


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
