"""
Type stubs for protocol buffer messages and services for the AddressBook pedagogical example.

This module is auto-generated from the person.proto file and provides type hints for all messages and services defined in the proto file. It is intended for use in educational and demonstration contexts, and helps with static analysis and editor support.

!!! note

    This file is generated code. Manual changes (except for documentation improvements) will be overwritten if the file is regenerated.
"""

# ruff: noqa: PGH004
# ruff: noqa
from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

DESCRIPTOR: _descriptor.FileDescriptor

class Person(_message.Message):
    """
    Represents a person in the AddressBook example.
    """

    __slots__ = ("email", "id", "name", "phones")
    class PhoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        """
        Enum for the type of phone number.
        """

        __slots__ = ()
        PHONE_TYPE_UNSPECIFIED: _ClassVar[Person.PhoneType]
        PHONE_TYPE_MOBILE: _ClassVar[Person.PhoneType]
        PHONE_TYPE_HOME: _ClassVar[Person.PhoneType]
        PHONE_TYPE_WORK: _ClassVar[Person.PhoneType]

    PHONE_TYPE_UNSPECIFIED: Person.PhoneType
    PHONE_TYPE_MOBILE: Person.PhoneType
    PHONE_TYPE_HOME: Person.PhoneType
    PHONE_TYPE_WORK: Person.PhoneType
    class PhoneNumber(_message.Message):
        """
        Represents a phone number for a person.
        """

        __slots__ = ("number", "type")
        NUMBER_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        number: str
        type: Person.PhoneType
        def __init__(
            self,
            number: _Optional[str] = ...,
            type: _Optional[_Union[Person.PhoneType, str]] = ...,
        ) -> None:
            """
            Create a new PhoneNumber instance.

            Args:
                number:
                    The phone number as a string.
                type:
                    The type of phone number (e.g., mobile, home, work).
            """

    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONES_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    email: str
    phones: _containers.RepeatedCompositeFieldContainer[Person.PhoneNumber]
    def __init__(
        self,
        name: _Optional[str] = ...,
        id: _Optional[int] = ...,
        email: _Optional[str] = ...,
        phones: _Optional[_Iterable[_Union[Person.PhoneNumber, _Mapping]]] = ...,
    ) -> None:
        """
        Creates a new Person instance.

        Args:
            name:
                The person's name.
            id:
                The unique identifier for the person.
            email:
                The person's email address.
            phones:
                A list of phone numbers for the person.
        """

class AddressBook(_message.Message):
    """
    Represents an address book containing multiple people.
    """

    __slots__ = ("people",)
    PEOPLE_FIELD_NUMBER: _ClassVar[int]
    people: _containers.RepeatedCompositeFieldContainer[Person]
    def __init__(
        self,
        people: _Optional[_Iterable[_Union[Person, _Mapping]]] = ...,
    ) -> None:
        """
        Creates a new AddressBook instance.

        Args:
            people: A list of Person objects in the address book.
        """

class GetPersonRequest(_message.Message):
    """
    Request message for retrieving a person by ID.
    """

    __slots__ = ("person_id",)
    PERSON_ID_FIELD_NUMBER: _ClassVar[int]
    person_id: int
    def __init__(self, person_id: _Optional[int] = ...) -> None:
        """
        Creates a new GetPersonRequest instance.

        Args:
            person_id:
                The unique identifier of the person to retrieve.
        """

class GetPersonResponse(_message.Message):
    """
    Response message containing a single person.
    """

    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None:
        """
        Creates a new GetPersonResponse instance.

        Args:
            person:
                The Person object returned by the service.
        """

class ListPeopleRequest(_message.Message):
    """
    Request message for listing all people in the address book.
    """

    __slots__ = ()
    def __init__(self) -> None:
        """
        Creates a new ListPeopleRequest instance.
        """

class ListPeopleResponse(_message.Message):
    """
    Response message containing a list of people.
    """

    __slots__ = ("people",)
    PEOPLE_FIELD_NUMBER: _ClassVar[int]
    people: _containers.RepeatedCompositeFieldContainer[Person]
    def __init__(
        self,
        people: _Optional[_Iterable[_Union[Person, _Mapping]]] = ...,
    ) -> None:
        """
        Creates a new ListPeopleResponse instance.

        Args:
            people:
                The list of Person objects returned by the service.
        """

class AddPersonRequest(_message.Message):
    """
    Request message for adding a new person to the address book.
    """

    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None:
        """
        Creates a new AddPersonRequest instance.

        Args:
            person:
                The Person object to add.
        """

class AddPersonResponse(_message.Message):
    """
    Response message confirming the addition of a person.
    """

    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None:
        """
        Creates a new AddPersonResponse instance.

        Args:
            person:
                The Person object that was added.
        """
