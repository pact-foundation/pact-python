---
description: "Pact V2"
applyTo: "/src/pact/v2/**"
---

# Pact V2 Legacy Code

-   These files provide backwards compatibility with version 2 of Pact Python.
-   They are in maintenance mode with only critical bug fixes being applied - no new features should be added.
-   When making changes:
    -   Preserve existing APIs and behavior to maintain backwards compatibility
    -   Prioritize minimal, targeted fixes over architectural improvements
    -   Ensure changes do not break existing user code
-   New development should focus on the main V3+ codebase in `/src/pact/` instead.
