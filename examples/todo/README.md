## Example Consumer and provider test using Pact V3 features

This is an example project with a test that uses V3 Pact features. It has an example test for both JSON
and XML format. It has been ported from the Pact-JS project.

## To run it

Using the beta version of Pact-Python with V3 support, you need to do the following:

1. In the root of the GitHub repo

```console
$ make deps
$ make package
```

2. Run the test

```console
$ make todo
```

## V3 features

This has 3 tests. The first uses generators and matchers for numbers and datetime values. The second 
test deals with XML responses. The last one posts an image to the provider.

## Enabling debug logs

The `PACT_LOG_LEVEL` environment variable controls the log output from the Rust libs.

```console
$ PACT_LOG_LEVEL=debug pytest --capture=no
```
