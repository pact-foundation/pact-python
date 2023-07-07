from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AreaRequest(_message.Message):
    __slots__ = ["shapes"]
    SHAPES_FIELD_NUMBER: _ClassVar[int]
    shapes: _containers.RepeatedCompositeFieldContainer[ShapeMessage]
    def __init__(self, shapes: _Optional[_Iterable[_Union[ShapeMessage, _Mapping]]] = ...) -> None: ...

class AreaResponse(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, value: _Optional[_Iterable[float]] = ...) -> None: ...

class Circle(_message.Message):
    __slots__ = ["radius"]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    radius: float
    def __init__(self, radius: _Optional[float] = ...) -> None: ...

class Parallelogram(_message.Message):
    __slots__ = ["base_length", "height"]
    BASE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    base_length: float
    height: float
    def __init__(self, base_length: _Optional[float] = ..., height: _Optional[float] = ...) -> None: ...

class Rectangle(_message.Message):
    __slots__ = ["length", "width"]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    length: float
    width: float
    def __init__(self, length: _Optional[float] = ..., width: _Optional[float] = ...) -> None: ...

class ShapeMessage(_message.Message):
    __slots__ = ["circle", "parallelogram", "rectangle", "square", "triangle"]
    CIRCLE_FIELD_NUMBER: _ClassVar[int]
    PARALLELOGRAM_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_FIELD_NUMBER: _ClassVar[int]
    SQUARE_FIELD_NUMBER: _ClassVar[int]
    TRIANGLE_FIELD_NUMBER: _ClassVar[int]
    circle: Circle
    parallelogram: Parallelogram
    rectangle: Rectangle
    square: Square
    triangle: Triangle
    def __init__(self, square: _Optional[_Union[Square, _Mapping]] = ..., rectangle: _Optional[_Union[Rectangle, _Mapping]] = ..., circle: _Optional[_Union[Circle, _Mapping]] = ..., triangle: _Optional[_Union[Triangle, _Mapping]] = ..., parallelogram: _Optional[_Union[Parallelogram, _Mapping]] = ...) -> None: ...

class Square(_message.Message):
    __slots__ = ["edge_length"]
    EDGE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    edge_length: float
    def __init__(self, edge_length: _Optional[float] = ...) -> None: ...

class Triangle(_message.Message):
    __slots__ = ["edge_a", "edge_b", "edge_c"]
    EDGE_A_FIELD_NUMBER: _ClassVar[int]
    EDGE_B_FIELD_NUMBER: _ClassVar[int]
    EDGE_C_FIELD_NUMBER: _ClassVar[int]
    edge_a: float
    edge_b: float
    edge_c: float
    def __init__(self, edge_a: _Optional[float] = ..., edge_b: _Optional[float] = ..., edge_c: _Optional[float] = ...) -> None: ...
