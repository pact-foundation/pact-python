---
authors:
    - JP-Ellis
date:
    created: 2024-05-02
---

# Integrating Rust FFI with Pact Python

In the [forthcoming release of Pact Python version 3](./04-11 a sneak peek into the pact python future.md), we're excited to be integrating our library with the ['Rust core'](https://github.com/pact-foundation/pact-reference), a Rust-based library that encapsulates Pact's fundamental operations for both consumers and providers. Known for its high performance and safety guarantees, [Rust](https://rust-lang.org) enables us to enhance the robustness and efficiency of our implementation. This move also promises simplified maintenance and scalability for future iterations of both the Pact Python library, and the [broader Pact ecosystem](https://docs.pact.io/diagrams/ecosystem).

At its essence, this Rust-powered engine handles critical tasks such as parsing and serializing Pact files, matching requests with responses, and generating new Pact contracts. It provides mocking capabilities to simulate a provider when verifying a consumer, and equally acts in reverse when replaying consumer requests against a provider. By adopting this shared core logic from Rust, we will achieve uniformity across all languages implementing Pact while streamlining the integration of enhancements or bug fixes-benefits across our diverse ecosystem.

In this blog post, I will delve into how this is all achieved. From explaining how [Hatch](https://hatch.pypa.io) is used to compile a binary extension and generate wheels for all supported platforms, to the intricacies of interfacing with the binary library. This information is not required to use Pact Python, but hopes to provide a deeper understanding of the inner workings of the library.

<!-- more -->

## Briding Python and Binary Libraries

Python, known for its dynamic typing and automated memory management, is fundamentally an interpreted language. Despite not having innate capabilities to directly interact with binary libraries, most Python interpreters bridge this gap efficiently. For instance, CPython—the principal interpreter—enables the creation of binary extensions[^1] and similarly, PyPy—a widely-used alternative—offers comparable functionalities[^2].

[^1]: You can find extensive documentation on building extensions for CPython [here](https://docs.python.org/3/extending/extending.html).
[^2]: PyPy extension-building documentation is available [here](https://doc.pypy.org/en/latest/extending.html).

However, each interpreter has a distinct API tailored for crafting these binary extensions, which unfortunately leads to a lack of universal solutions across different environments. Furthermore, interpreters like [Jython](https://jython.org) and [Pyodide](https://pyodide.org/en/stable/), which are based on Java and WebAssembly respectively, present unique challenges that often preclude the straightforward use of such extensions due to their distinct runtime architectures.[^3]

[^3]: It would appear that Pyodide can support C extensions as explained [here](https://pyodide.org/en/stable/development/new-packages.html), though by and large Pyodide appears to be intended for pure Python packages.

While it is possible for the extension to contain all the logic, our specific requirement is merely to provide a bridge between Python and the Rust core library. This is the niche that [Python C Foreign Function Interface (CFFI)](https://cffi.readthedocs.io/en/stable/) fills. By parsing a C header file, CFFI automates the generation of extension code needed for Python to interface with the binary library. Consequently, this library can be imported into Python as if it were any standard module—streamlining development and potentially improving performance by leveraging optimized native code.

Moreover, CFFI offers a simpler and more maintainable approach compared to other methods requiring manual boilerplate code. It abstracts away many of the complexities associated with linking Python to C libraries, making it an attractive choice for developers looking for efficiency and ease of integration.

## Building the Python Extension

Pact Python uses the fantastic [Hatch](https://hatch.pypa.io) project management and build system for handling dependencies, project metadata, and generate wheels across all supported platforms. Hatch can be extensively customised to suit the needs of each project through its configuration, plugin system, and ability to define custom interfaces.

In the case of Pact Python, a [`BuildHookInterface`](https://hatch.pypa.io/1.9/plugins/build-hook/reference/) is defined in [`hatch_build.py`](https://github.com/pact-foundation/pact-python/blob/d6869797b52429252b5d0da4d0fc0079f9d3671c/hatch_build.py) which executes several crucial tasks:

1.  Downloads a specified version of the Rust core library from a designated release on the Pact Foundation's GitHub repository, including the accompanying `pact.h` header file.
2.  Utilizes CFFI to create a Python extension module that encapsulates the Rust core library:

    ```python
    ffibuilder = cffi.FFI()
    with (self.tmpdir / "pact.h").open("r", encoding="utf-8") as f:
        ffibuilder.cdef(f.read())  # (1)
    ffibuilder.set_source(
        "_ffi",  # (2)
        "\n".join([*includes, '#include "pact.h"']),
        libraries=["pact_ffi", *extra_libs],  # (3)
        library_dirs=[str(self.tmpdir)],  # (4)
    )
    output = Path(ffibuilder.compile(verbose=True, tmpdir=str(self.tmpdir)))  # (5)
    shutil.copy(output, PACT_ROOT_DIR / "v3")
    ```

    1.  The `cdef` method processes the contents of `pact.h`, creating necessary declarations for the Python extension.
    2.  Names the extension module `_ffi`, which is subsequently importable in Python via `import _ffi`.
    3.  Details libraries to be linked, including `pact_ffi` and platform-specific additional libraries (`extra_libs`) as needed.
    4.  Defines the directory that holds the Rust code library.
    5.  Compiles the extension module and then relocates it to the Pact Python project directory.

Upon completion of these steps, Hatch produces a Python extension module that interfaces seamlessly with the Rust core library. It will have a filename like `src/pact/v3/_ffi.cpython-312-darwin.so` (for CPython 3.12 on macOS) which can be used just as any other Python module. That is, the binary `_ffi` file can be imported in the same way as one would import a regular `.py` file.

## Using the CFFI Extension

With the Python extension module built, developers have direct access to interact with the Rust core library from their Python code. This is made possible through two main components generated by CFFI:

1.  `lib`, which provides access to functions and data structures from the Rust core library;
2.  `ffi`, which offers additional utilities on the Python side for interfacing with these Rust components.

Let's look at a simple example of using the CFFI extension to invoke the `pactffi_version` function from the Rust core library:

```python
from _ffi import lib, ffi

version = lib.pactffi_version()  # (1)
version = ffi.string(version)  # (2)
if isinstance(version, bytes):  # (3)
    version = version.decode("utf-8")
```

1.  Call the `pactffi_version` function from Rust, which returns a pointer to a null-terminated string. This is represented in Python as a `cdata 'char *'` object.
2.  Convert the pointer to a Python string, or bytes if necessary, using the `ffi.string` method.
3.  Decode the bytes to a string if needed.

While the process is reasonably straightforward, it does require some boilerplate code to handle the type conversions. To simplify this, we've wrapped each function from the Rust core library in a simple Python function that performs these conversion autoamtically. You can find these wrapper functions in the [`ffi` module](https://github.com/pact-foundation/pact-python/blob/d6869797b52429252b5d0da4d0fc0079f9d3671c/src/pact/v3/ffi.py). For example, the `version` function is implemented as follows:

```python
def version() -> str:
    """
    Return the version of the pact_ffi library.

    [Rust `pactffi_version`](https://docs.rs/pact_ffi/0.4.19/pact_ffi/?search=pactffi_version)

    Returns:
        The version of the pact_ffi library as a string, in the form of `x.y.z`.
    """
    v = ffi.string(lib.pactffi_version())
    if isinstance(v, bytes):
        return v.decode("utf-8")
    return v
```

The majority of the Rust core library functions return some trivial data types (booleans and integers) which are transparently handled by CFFI without the need for additional conversions. However, there typically is still a need to appropriately manage conversion of arguments into the expected types. A typical pattern will be converting an `str | None` into a `cdata 'char *'`, where `None` is represented as a null pointer:

```python
def foobar(value: str | None) -> bool:
    return lib.foobar(value.encode("utf-8") if value else ffi.NULL)  # (1)
```

1.  The encoding of the string to UTF-8 ensures that the string is correctly represented in the Rust core library.

### Error Handling

Handling errors across programming languages can be challenging due to differences in error handling mechanisms. The Rust programming language has two methods of handling unexpected errors:

1.  **Panicking**: This typically occurs when a function encounters an unrecoverable error and terminates the program. The Rust core library handles panics by catching them before they propagate to the Python interpreter, and therefore they can be safely ignored.

2.  **Result**: This is a more structured approach whereby a function can return either `Ok(value)` or `Err(error)` to indicate success or failure.

It is unfortunately difficult for the C foreign function interface to handle Rust's `Result` type directly. Instead, we've opted to using return codes, either in the form of a boolean or an integer, to indicate success or failure. This is a common pattern in C libraries and is easily translated into Python:

```python
def write_pact_file(
    mock_server_handle: PactServerHandle,
    directory: str | Path,
    *,
    overwrite: bool,
) -> None:
    ret: int = lib.pactffi_write_pact_file(
        mock_server_handle._ref,
        str(directory).encode("utf-8"),
        overwrite,
    )
    if ret == 0:
        return  # (1)
    if ret == 1:
        msg = (
            f"The function panicked while writing the Pact for {mock_server_handle} in"
            f" {directory}."
        )
    elif ret == 2:
        msg = (
            f"The Pact file for {mock_server_handle} could not be written in"
            f" {directory}."
        )
    else:
        msg = (
            "An unknown error occurred while writing the Pact for"
            f" {mock_server_handle} in {directory}."
        )
    raise RuntimeError(msg)
```

1.  A return code of `0` indicates success, and the function returns without raising an exception. Other return codes indicate different types of errors, which are then translated into Python exceptions.

By ensuring that the return codes are correctly handled, we can ensure that end-users are aware of any issues that arise during the execution of the Rust core library functions in a Pythonic manner.

### Memory Management

Memory management is another critical aspect to consider when interfacing with binary libraries. Rust's memory model is based on ownership and borrowing, which ensures memory safety and eliminates the need for manual memory management. When interfacing with other languages though, Rust cannot guarantee memory safety, and additional care must be taken to prevent memory leaks. Python, on the other hand, relies on garbage collection to manage memory automatically, which works by checking whether an object is still reachable and deallocating it if not.

In the case of the Rust core library, the ability to deallocate memory is provided by specific functions such as `pactffi_string_delete`. Python also offers a mechanism to hook into the garbage collection process using the `__del__` method. A good example of this is the `OwnedString` class from the `ffi` module, which automatically deallocates memory when the object is no longer reachable:

```python
class OwnedString(str):
    def __new__(cls, ptr: cffi.FFI.CData) -> Self:
        s = ffi.string(ptr)
        return super().__new__(
            cls,
            s if isinstance(s, str) else s.decode("utf-8"),
        )

    def __del__(self) -> None:
        lib.pactffi_string_delete(self._ptr)
```

The `__del__` method is called[^4] when the object is about to be deallocated[^5], allowing us to free the memory associated with the string. This ensures that memory is managed correctly and prevents potential memory leaks.

[^4]: There are some unique circumstances where `__del__` may not be called, such as when the Python interpreter is shutting down.
[^5]: Python does not provide guarantees on when `__del__` will be called, so it is not recommended to rely on it for critical cleanup tasks. Instead, the `__enter__` and `__exit__` methods should be used to guarantee timely cleanup.

## Conclusion

Integrating Pact Python with the Rust FFI represents a significant step towards enhancing the robustness and efficiency of our library. With the release of version 3 of Pact Python, it is our hope that the community will greatly benefit from the improved performance provided by the Rust core library.

It is our hope that this blog post also helps to shed some light on the inner workings of the library, whether you are a Pact user who is curious about how the library functions, or a developer looking to contribute to the project.
