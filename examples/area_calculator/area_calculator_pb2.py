# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: area_calculator.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x61rea_calculator.proto\x12\x0f\x61rea_calculator\"\x86\x02\n\x0cShapeMessage\x12)\n\x06square\x18\x01 \x01(\x0b\x32\x17.area_calculator.SquareH\x00\x12/\n\trectangle\x18\x02 \x01(\x0b\x32\x1a.area_calculator.RectangleH\x00\x12)\n\x06\x63ircle\x18\x03 \x01(\x0b\x32\x17.area_calculator.CircleH\x00\x12-\n\x08triangle\x18\x04 \x01(\x0b\x32\x19.area_calculator.TriangleH\x00\x12\x37\n\rparallelogram\x18\x05 \x01(\x0b\x32\x1e.area_calculator.ParallelogramH\x00\x42\x07\n\x05shape\"\x1d\n\x06Square\x12\x13\n\x0b\x65\x64ge_length\x18\x01 \x01(\x02\"*\n\tRectangle\x12\x0e\n\x06length\x18\x01 \x01(\x02\x12\r\n\x05width\x18\x02 \x01(\x02\"\x18\n\x06\x43ircle\x12\x0e\n\x06radius\x18\x01 \x01(\x02\":\n\x08Triangle\x12\x0e\n\x06\x65\x64ge_a\x18\x01 \x01(\x02\x12\x0e\n\x06\x65\x64ge_b\x18\x02 \x01(\x02\x12\x0e\n\x06\x65\x64ge_c\x18\x03 \x01(\x02\"4\n\rParallelogram\x12\x13\n\x0b\x62\x61se_length\x18\x01 \x01(\x02\x12\x0e\n\x06height\x18\x02 \x01(\x02\"<\n\x0b\x41reaRequest\x12-\n\x06shapes\x18\x01 \x03(\x0b\x32\x1d.area_calculator.ShapeMessage\"\x1d\n\x0c\x41reaResponse\x12\r\n\x05value\x18\x01 \x03(\x02\x32\xad\x01\n\nCalculator\x12N\n\x0c\x63\x61lculateOne\x12\x1d.area_calculator.ShapeMessage\x1a\x1d.area_calculator.AreaResponse\"\x00\x12O\n\x0e\x63\x61lculateMulti\x12\x1c.area_calculator.AreaRequest\x1a\x1d.area_calculator.AreaResponse\"\x00\x42\x1cZ\x17io.pact/area_calculator\xd0\x02\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'area_calculator_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\027io.pact/area_calculator\320\002\001'
  _SHAPEMESSAGE._serialized_start=43
  _SHAPEMESSAGE._serialized_end=305
  _SQUARE._serialized_start=307
  _SQUARE._serialized_end=336
  _RECTANGLE._serialized_start=338
  _RECTANGLE._serialized_end=380
  _CIRCLE._serialized_start=382
  _CIRCLE._serialized_end=406
  _TRIANGLE._serialized_start=408
  _TRIANGLE._serialized_end=466
  _PARALLELOGRAM._serialized_start=468
  _PARALLELOGRAM._serialized_end=520
  _AREAREQUEST._serialized_start=522
  _AREAREQUEST._serialized_end=582
  _AREARESPONSE._serialized_start=584
  _AREARESPONSE._serialized_end=613
  _CALCULATOR._serialized_start=616
  _CALCULATOR._serialized_end=789
# @@protoc_insertion_point(module_scope)
