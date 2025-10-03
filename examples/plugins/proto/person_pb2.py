# ruff: noqa: PGH004
# ruff: noqa
# source: person.proto
# Protobuf Python Version: 6.31.0
"""
Protocol buffer message and service definitions for the AddressBook pedagogical example.

This module is auto-generated from the person.proto file using the protobuf compiler. It provides Python classes for all messages and services defined in the proto file, and is intended for use in educational and demonstration contexts.

!!! note

    This file is generated code. Manual changes (except for documentation improvements) will be overwritten if the file is regenerated.
"""

from __future__ import annotations

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 6, 31, 0, "", "person.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cperson.proto\x12\x06person"\x9f\x02\n\x06Person\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\x12\r\n\x05\x65mail\x18\x03 \x01(\t\x12*\n\x06phones\x18\x04 \x03(\x0b\x32\x1a.person.Person.PhoneNumber\x1aV\n\x0bPhoneNumber\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x37\n\x04type\x18\x02 \x01(\x0e\x32\x18.person.Person.PhoneType:\x0fPHONE_TYPE_HOME"h\n\tPhoneType\x12\x1a\n\x16PHONE_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11PHONE_TYPE_MOBILE\x10\x01\x12\x13\n\x0fPHONE_TYPE_HOME\x10\x02\x12\x13\n\x0fPHONE_TYPE_WORK\x10\x03"-\n\x0b\x41\x64\x64ressBook\x12\x1e\n\x06people\x18\x01 \x03(\x0b\x32\x0e.person.Person"%\n\x10GetPersonRequest\x12\x11\n\tperson_id\x18\x01 \x01(\x05"3\n\x11GetPersonResponse\x12\x1e\n\x06person\x18\x01 \x01(\x0b\x32\x0e.person.Person"\x13\n\x11ListPeopleRequest"4\n\x12ListPeopleResponse\x12\x1e\n\x06people\x18\x01 \x03(\x0b\x32\x0e.person.Person"2\n\x10\x41\x64\x64PersonRequest\x12\x1e\n\x06person\x18\x01 \x01(\x0b\x32\x0e.person.Person"3\n\x11\x41\x64\x64PersonResponse\x12\x1e\n\x06person\x18\x01 \x01(\x0b\x32\x0e.person.Person2\xdd\x01\n\x12\x41\x64\x64ressBookService\x12@\n\tGetPerson\x12\x18.person.GetPersonRequest\x1a\x19.person.GetPersonResponse\x12\x43\n\nListPeople\x12\x19.person.ListPeopleRequest\x1a\x1a.person.ListPeopleResponse\x12@\n\tAddPerson\x12\x18.person.AddPersonRequest\x1a\x19.person.AddPersonResponseb\x08\x65\x64itionsp\xe8\x07'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "person_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_PERSON"]._serialized_start = 25
    _globals["_PERSON"]._serialized_end = 312
    _globals["_PERSON_PHONENUMBER"]._serialized_start = 120
    _globals["_PERSON_PHONENUMBER"]._serialized_end = 206
    _globals["_PERSON_PHONETYPE"]._serialized_start = 208
    _globals["_PERSON_PHONETYPE"]._serialized_end = 312
    _globals["_ADDRESSBOOK"]._serialized_start = 314
    _globals["_ADDRESSBOOK"]._serialized_end = 359
    _globals["_GETPERSONREQUEST"]._serialized_start = 361
    _globals["_GETPERSONREQUEST"]._serialized_end = 398
    _globals["_GETPERSONRESPONSE"]._serialized_start = 400
    _globals["_GETPERSONRESPONSE"]._serialized_end = 451
    _globals["_LISTPEOPLEREQUEST"]._serialized_start = 453
    _globals["_LISTPEOPLEREQUEST"]._serialized_end = 472
    _globals["_LISTPEOPLERESPONSE"]._serialized_start = 474
    _globals["_LISTPEOPLERESPONSE"]._serialized_end = 526
    _globals["_ADDPERSONREQUEST"]._serialized_start = 528
    _globals["_ADDPERSONREQUEST"]._serialized_end = 578
    _globals["_ADDPERSONRESPONSE"]._serialized_start = 580
    _globals["_ADDPERSONRESPONSE"]._serialized_end = 631
    _globals["_ADDRESSBOOKSERVICE"]._serialized_start = 634
    _globals["_ADDRESSBOOKSERVICE"]._serialized_end = 855
# @@protoc_insertion_point(module_scope)
