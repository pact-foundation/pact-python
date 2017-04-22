DOCS_DIR := ./docs

define VERSION_CHECK
import setup
import pact
msg = 'pact.__version__ must match the last version in CHANGES.txt'
assert setup.get_version() == pact.__version__, msg
endef


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


.PHONY: e2e
e2e:
	sh -c '\
		cd e2e; \
		docker-compose pull > /dev/null; \
		docker-compose up -d pactmockservice; \
		while ! nc -z localhost 1234; do sleep 0.1; done; \
		docker-compose logs --follow > ./pacts/mock-service-logs.txt & \
		nosetests ./contracts; \
		docker-compose down; \
		docker-compose up -d app pactverifier; \
		docker-compose logs --follow >> ./pact/verifier-logs.txt & \
		docker-compose exec pactverifier bundle exec rake verify_pacts; \
		docker-compose down'

.PHONY: package
package: pact/bin
	python setup.py sdist


pact/bin:
	scripts/build.sh


export VERSION_CHECK
.PHONY: test
test: deps pact/bin
	@echo "Checking version consistency..."
	python -c "$$VERSION_CHECK"

	@echo "flake8..."
	flake8

	@echo "pydocstyle..."
	pydocstyle pact

	@echo "testing..."
	tox
