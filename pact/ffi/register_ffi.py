"""Registers our FFI library."""
import platform
import os
import sys

class RegisterFfi(object):
    """Registers our FFI library."""

    IS_64 = sys.maxsize > 2 ** 32

    DIRECTIVES = [
        "#ifndef pact_ffi_h",
        "#define pact_ffi_h",
        "#include <stdarg.h>",
        "#include <stdbool.h>",
        "#include <stdint.h>",
        "#include <stdlib.h>",
        "#endif /* pact_ffi_h */"
    ]
    FFI_LIB_PATH = os.path.abspath(os.getenv('PACT_FFI_PATH', os.path.join("pact", "bin")))

    FFI_HEADER_PATH = os.path.join(FFI_LIB_PATH, "pact.h")

    def process_pact_header_file(self, file):
        """Process the pact header file."""
        with open(file, "r") as fp:
            lines = fp.readlines()

        pactfile = []

        for line in lines:
            if line.strip("\n") not in self.DIRECTIVES:
                pactfile.append(line)

        return ''.join(pactfile)

    def load_ffi_library(self, ffi):
        """Load the right library."""
        target_platform = platform.platform().lower()
        print(target_platform)
        print(platform.machine())

        if ("darwin" in target_platform or "macos" in target_platform) and ("aarch64" in platform.machine() or "arm64" in platform.machine()):
            # libname = os.path.abspath("pact/bin/libpact_ffi-osx-aarch64-apple-darwin.dylib")
            libname = os.path.join(self.FFI_LIB_PATH, "libpact_ffi-osx-aarch64-apple-darwin.dylib")
            # libname = os.path.abspath("pact/bin/libpact_ffi-osx-aarch64-apple-darwin.dylib")
        elif "darwin" in target_platform or "macos" in target_platform:
            libname = os.path.abspath(self.FFI_LIB_PATH, "libpact_ffi-osx-x86_64.dylib")
        elif "linux" in target_platform and self.IS_64 and ("aarch64" in platform.machine() or "arm64" in platform.machine()):
            libname = os.path.abspath(self.FFI_LIB_PATH, "libpact_ffi-linux-aarch64.so")
        elif "linux" in target_platform and self.IS_64:
            libname = os.path.abspath(self.FFI_LIB_PATH, "libpact_ffi-linux-x86_64.so")
        elif 'windows' in target_platform:
            libname = os.path.abspath(self.FFI_LIB_PATH, "pact_ffi-windows-x86_64.dll")
        else:
            msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
                   ' Windows, and OSX are currently supported.').format(target_platform)
            raise Exception(msg)

        return ffi.dlopen(libname)

    def load_ffi_headers(self, ffi):
        """Load the FFI headers."""
        return ffi.cdef(self.process_pact_header_file(self.FFI_HEADER_PATH))

    def get_ffi_lib(self, ffi):
        """Load the FFI library."""
        self.load_ffi_headers(ffi)
        lib = self.load_ffi_library(ffi)
        return lib
