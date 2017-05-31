DOCS_DIR := ./docs


help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  deps       to install the required files for development"
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
	pip install -r requirements_dev.txt


define E2E
	set -e
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
	pact-verifier \
		--provider-base-url=http://localhost:5000 \
		--pact-urls=./pacts/consumer-provider.json \
		--provider-states-url=http://localhost:5000/_pact/provider-states \
		--provider-states-setup-url=http://localhost:5000/_pact/provider-states/active
endef


export E2E
.PHONY: e2e
e2e:
	sh -c "$$E2E"


.PHONY: package
package: pact/bin
	python setup.py sdist


pact/bin:
	scripts/build.sh


.PHONY: test
test: deps pact/bin
	flake8
	pydocstyle pact
	coverage erase
	tox
	coverage report --fail-under=100
