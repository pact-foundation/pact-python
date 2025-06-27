r"""
Protocol Buffers (protobuf) support for Pact Python examples.

This module contains the generated Python code from the protobuf definition in
`person.proto`, which is used by both the `protobuf` and `grpc` examples. These
examples are designed to be pedagogical, demonstrating how to use Pact for
contract testing with Protocol Buffers and gRPC services.

## What is Protocol Buffers (protobuf)?

Protocol Buffers (protobuf) is Google's language-neutral, platform-neutral,
extensible mechanism for serializing structured data. Think of it like XML or
JSON, but smaller, faster, and simpler. You define your data structures in a
`.proto` file, and then use the protobuf compiler to generate classes in your
programming language of choice.

For the purposes of our examples, we define `person.proto` which defines the
following messages:

-   `Person`: Represents a person with name, ID, email, and phone numbers
-   `AddressBook`: A collection of Person objects
-   Request/Response messages for service operations:

    -   `GetPersonRequest/Response`: For retrieving a person by ID
    -   `ListPeopleRequest/Response`: For listing all people
    -   `AddPersonRequest/Response`: For adding a new person

The file also defines a single service (useful for the gRPC example):

-   `AddressBookService`: Defines gRPC service methods for managing an address
    book

## Generated Files

The `.proto` file is used by `protoc` and other tools to generate Python code.
The three files present in this directory can be generated using:

```bash
python -m grpc_tools.protoc \
    -I. \ # (1)
    --python_out=. \  # (2)
    --pyi_out=. \  # (3)
    --grpc_python_out=. \  # (4)
    person.proto
```

1.  `-I.` is used by the gRPC code generator to allow it to import the
    `person_pb2` module.
2.  `--python_out=.` specifies the output directory for the generated Python
    code files.
3.  `--pyi_out=.` specifies the output directory for the generated Python stub
    files.
4.  `--grpc_python_out=.` specifies the output directory for the generated gRPC
    service files.

### `person_pb2.py`

**Purpose**: Contains the core protobuf message classes and serialization logic.

**What it does**:

-   Defines Python classes for each protobuf message (Person, AddressBook, etc.)
-   Provides methods for serializing objects to binary format
    (`SerializeToString()`)
-   Provides methods for deserializing binary data back to objects
    (`ParseFromString()`)
-   Handles all the low-level protobuf protocol details

### `person_pb2.pyi`

**Purpose**: Type stub file providing type hints for better IDE support and
static analysis.

**What it does**:

-   Provides type annotations for all generated classes and methods
-   Enables better autocomplete and type checking in IDEs like VSCode or PyCharm
-   Helps static type checkers like mypy understand the generated code
-   Makes the code more maintainable and less error-prone

### `person_pb2_grpc.py`

**Purpose**: Contains gRPC service client and server classes.

**What it does**:

-   Defines client stub classes for calling gRPC services
-   Defines server base classes for implementing gRPC services
-   Handles the gRPC protocol layer (HTTP/2, streaming, etc.)
-   Maps protobuf messages to gRPC method calls

## Learning Resources

For more information about Protocol Buffers and gRPC:

-   [Protocol Buffers
    Tutorial](https://protobuf.dev/getting-started/pythontutorial/)
-   [gRPC Python Tutorial](https://grpc.io/docs/languages/python/)
-   [Pact gRPC/Protobuf Plugin](https://github.com/pactflow/pact-protobuf-plugin)
"""
