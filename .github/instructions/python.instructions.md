---
description: "Python coding conventions and guidelines"
applyTo: "**/*.py"
---

# Python Coding Conventions

## Documentation

-   MkDocs-Material is used for documentation generation, allowing for Markdown formatting in docstrings.
-   All functions must have Google-style, Markdown-compatible docstrings with proper formatting (note whitespace and indentation as shown):

    ```python
    def function_name(param1: Type1, param2: Type2) -> ReturnType:
        """
        Brief description of the function.

        Optional detailed description of the function.

        Args:
            param1:
                Description of param1.

            param2:
                Description of param2.

        Returns:
            Description of the return value.
        """
    ```

-   References to other functions, classes, or modules must be linked, using the fully qualified Python path:

    ```markdown
    A link to a [`ClassName.method`][pact.module.ClassName.method] or a
    [`function_name`][pact.module.function_name].
    ```

## General Instructions

-   Always prioritize readability and clarity.
-   All functions must use type annotations for parameters and return types. Prefer generic types (e.g., `Iterable[str]`, `Mapping[str, int]`) over concrete types (`list[str]`, `dict[str, int]`) for better flexibility and reusability.
-   Write code with good maintainability practices, including comments on why certain design decisions were made.
-   Handle edge cases and write clear exception handling.
-   Write concise, efficient, and idiomatic code that is also easily understandable.
-   When performing validations, use early returns to reduce nesting and improve readability.
    -   Prefer built-in exceptions (such as `ValueError` for invalid values, `TypeError` for incorrect types, etc.) for standard Python errors.
    -   For Pact-specific issues, define and use custom exceptions to provide clear and meaningful error handling. These must all inherit from the `PactError` base class, and may inherit from other exceptions as appropriate.

## Code Style and Linting

-   Use `ruff` for linting and formatting, preferring automatic fixes where possible.
