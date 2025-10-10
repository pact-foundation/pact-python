---
description: "Pact CLI"
applyTo: "/pact-python-cli/**"
---

# Pact CLI

-   This directory contains the source for the `pact-python-cli` package, which provides a thin wrapper around the Pact CLI binaries.
-   It allows users to install the Pact CLI tools via PyPI and use them in Python projects without requiring separate installation steps.
-   The package includes executable wrappers for all major Pact CLI tools (`pact`, `pact-broker`, `pact-message`, `pact-mock-service`, `pact-provider-verifier`, etc.).
-   By default, it uses bundled binaries, but can fall back to system-installed Pact CLI tools when `PACT_USE_SYSTEM_BINS` environment variable is set to `TRUE` or `YES`.
