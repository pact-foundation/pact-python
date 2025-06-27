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
    __slots__ = ("email", "id", "name", "phones")
    class PhoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
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
        __slots__ = ("number", "type")
        NUMBER_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        number: str
        type: Person.PhoneType
        def __init__(
            self,
            number: _Optional[str] = ...,
            type: _Optional[_Union[Person.PhoneType, str]] = ...,
        ) -> None: ...

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
    ) -> None: ...

class AddressBook(_message.Message):
    __slots__ = ("people",)
    PEOPLE_FIELD_NUMBER: _ClassVar[int]
    people: _containers.RepeatedCompositeFieldContainer[Person]
    def __init__(
        self, people: _Optional[_Iterable[_Union[Person, _Mapping]]] = ...
    ) -> None: ...

class GetPersonRequest(_message.Message):
    __slots__ = ("person_id",)
    PERSON_ID_FIELD_NUMBER: _ClassVar[int]
    person_id: int
    def __init__(self, person_id: _Optional[int] = ...) -> None: ...

class GetPersonResponse(_message.Message):
    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None: ...

class ListPeopleRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPeopleResponse(_message.Message):
    __slots__ = ("people",)
    PEOPLE_FIELD_NUMBER: _ClassVar[int]
    people: _containers.RepeatedCompositeFieldContainer[Person]
    def __init__(
        self, people: _Optional[_Iterable[_Union[Person, _Mapping]]] = ...
    ) -> None: ...

class AddPersonRequest(_message.Message):
    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None: ...

class AddPersonResponse(_message.Message):
    __slots__ = ("person",)
    PERSON_FIELD_NUMBER: _ClassVar[int]
    person: Person
    def __init__(self, person: _Optional[_Union[Person, _Mapping]] = ...) -> None: ...
