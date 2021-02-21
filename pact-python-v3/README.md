## Building the V3 wheel

```
maturin build
```

If openssl needs to be statically linked in

```
OPENSSL_STATIC=1 OPENSSL_LIB_DIR=/usr/lib/x86_64-linux-gnu OPENSSL_INCLUDE_DIR=/usr/include/openssl maturin build
```
