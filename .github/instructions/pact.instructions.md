---
description: "Pact Core Library"
applyTo: "/src/pact/**"
---

# Pact Core Library

-   The code in `src/pact/` forms the core Pact library that provides the main user-facing APIs.
-   This is the primary codebase for Pact Python functionality.
-   Key modules include:
    -   `pact.py` - Main Pact class for consumer testing
    -   `verifier.py` - Provider verification functionality
    -   `match/` - Matching rules and matchers
    -   `generate/` - Value generators
    -   `interaction/` - Interaction building blocks

## V2 Legacy Code

-   Files in `v2/` subdirectories implement the legacy version of Pact Python
-   This version is in maintenance mode with only critical bug fixes being applied
-   New features and active development should focus on the main codebase
