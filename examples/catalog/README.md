# Pact Patterns Catalog

This catalog contains focused, well-documented code snippets demonstrating specific Pact patterns and use cases. Unlike the full examples in the parent directory, catalog entries are designed to showcase a single pattern or technique with minimal application context.

## Available

-   [Multipart Form Data with Matching Rules](./multipart_matching_rules/README.md)

## Using Catalog Entries

Catalog entries are intended as a reference for learning and adapting Pact patterns. To get the most value:

-   **Read the documentation** in each entry's README to understand the pattern and its intended use.
-   **Review the code** to see how the pattern is implemented in practice.
-   **Explore the tests** to see example usages and edge cases.

If you want to experiment or adapt a pattern, you can run the tests for any entry:

```console
cd examples/catalog
uv run --group test pytest <catalog_entry_directory>
```

## Contributing Patterns

When adding a new catalog entry:

1.  Focus on a single pattern or technique
2.  Provide minimal but complete code, emphasizing the Pact aspects over application logic
3.  Document the pattern thoroughly
4.  Include working pytest tests
5.  Add it to this README

For complete examples with full application context, consider adding to the main examples directory instead.
