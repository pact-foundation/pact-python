---
description: "Python testing conventions and guidelines"
applyTo: "**/tests/**/*.py"
---

# Python Testing Conventions

-   Use `pytest` as the testing framework, with all tests located in `tests/` directories and files prefixed with `test_`.
-   Prefer descriptive function names that clearly indicate the test's purpose. Include docstrings only when additional context is needed beyond the function name.
-   Use `@pytest.mark.parametrize` to cover multiple scenarios without code duplication:

    ```python
    @pytest.mark.parametrize(
        ("param1", "param2", "expected"),
        [
            pytest.param(v1, x1, r1, id="description1"),
            pytest.param(v2, x2, r2, id="description2"),
            ...
        ]
    )
    def test_function(param1: Type1, param2: Type2, expected: ReturnType) -> None:
        ...
    ```

-   Ensure test coverage for:
    -   Critical application paths and core functionality
    -   Common edge cases (empty inputs, invalid data types, boundary conditions)
    -   Error conditions and exception handling
-   Include comments explaining complex test logic or edge case rationale.
-   Minimize mocking and prefer testing with real data and dependencies when practical. Mock only external services or components that are unreliable or expensive to test against.
-   Use pytest fixtures for common test setup and shared data.
