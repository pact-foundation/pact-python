DOCS_DIR := ./docs


help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  deps       to install the required files for development"
	@echo "  e2e        to run the end to end tests"
	@echo "  verifier   to run the verifier end to end tests"
	@echo "  examples   to run the example end to end tests"
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
	echo "e2e make"
	cd examples/e2e
  pip install -r requirements.txt
  pip install -e ../../
  pytest --pubish-pact ${TRAVIS_COMMIT}
  ./verify_pact.sh
endef
export E2E

.PHONY: e2e
e2e:
	bash -c "$$E2E"

.PHONY: examples
examples: e2e
	


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
