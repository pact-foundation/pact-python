help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  package    to build a wheel and sdist"
	@echo "  release    to perform a release build, including deps, test, and package targets"
	@echo ""
	@echo "  test       to run all tests on the current python version"
	@echo "  test-all   to run all tests on all supported python versions"
	@echo "  example    to run the example end to end tests (requires docker)"
	@echo "  lint       to run the lints"
	@echo "  ci         to run test and lints"
	@echo ""
	@echo "  help       to show this help message"
	@echo ""
	@echo "Most of these targets are just wrappers around hatch commands."
	@echo "See https://hatch.pypa.org for information to install hatch."


.PHONY: release
release: clean test package


.PHONY: clean
clean:
	hatch clean


.PHONY: package
package:
	hatch build


.PHONY: test
test:
	hatch run test
	hatch run coverage report -m --fail-under=100


.PHONY: test-all
test-all:
	hatch run test:test


.PHONY: example
example:
	hatch run example


.PHONY: lint
lint:
	hatch run lint
	hatch run format
	hatch run typecheck


.PHONY: ci
ci: test lint
