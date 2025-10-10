---
description: "Pact FFI"
applyTo: "/pact-python-ffi/**"
---

# Pact FFI

-   This directory contains the source for the `pact-python-ffi` package, which provides Python bindings to the Pact FFI library.
-   This library only exposes low-level FFI bindings and is not intended for direct use by end users. All user-facing functionality should be provided through the higher-level `pact` package.
-   Code in this package should focus exclusively on:
    -   Providing automatic memory management for FFI objects (implementing `__del__` methods to drop/free objects as needed)
    -   Converting between Python types and FFI types (input parameter casting and return value conversion)
    -   Handling errors returned from the FFI and converting them into appropriate Python exceptions
    -   Wrapping low-level C structs and handles in Python classes with proper lifecycle management
-   Avoid implementing high-level business logic or convenience methods - these belong in the main `pact` package.
