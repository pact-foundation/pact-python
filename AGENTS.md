# Pact Python - Quick Reference for AI Agents

## Commands

-   **Test**: `hatch run test` (all tests) or call `pytest` directly.
-   **Lint**: `hatch run lint --fix` (check+fix) or `hatch run format` (auto-fix)
-   **Typecheck**: `hatch run typecheck` (all)
-   **Examples**: `hatch run example` (run example tests)
-   **All checks**: `hatch run all` (format, lint, test, typecheck)
-   **V2 tests**: `hatch run v2-test:test` (legacy v2 compatibility tests)

## Code Style

-   **Imports**: Use generic types (`Iterable`, `Sequence`, `Mapping`) over concrete (`list`, `dict`). Absolute imports only (no relative).
-   **Types**: All functions require type annotations. Use `typing` module for generics.
-   **Docstrings**: Google-style with Markdown formatting. Link references: `[ClassName.method][pact.module.ClassName.method]`
-   **Formatting**: Use `ruff` for linting/formatting.
-   **Naming**: Follow PEP 8. Use descriptive names that indicate purpose.
-   **Error handling**: Use built-in exceptions (`ValueError`, `TypeError`) for standard errors. Custom exceptions inherit from `PactError`.
-   **Validation**: Use early returns to reduce nesting.
-   **Comments**: Explain design decisions, not what code does. No comments unless necessary.

## Testing

-   **Framework**: `pytest` with files prefixed `test_`. Use `@pytest.mark.parametrize` for multiple scenarios.
-   **Coverage**: Focus on critical paths, edge cases, error conditions.
-   **Fixtures**: Use pytest fixtures for shared setup. Minimize mocking.

## Project Structure

-   `src/pact/`: Main V3+ codebase (active development)
-   `src/pact/v2/`: Legacy V2 code (maintenance only - no new features)
-   `pact-python-ffi/`: Low-level FFI bindings (memory management, type conversion only)
-   `pact-python-cli/`: CLI wrapper (bundled binaries with system fallback)
