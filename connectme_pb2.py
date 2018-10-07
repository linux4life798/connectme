# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: connectme.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='connectme.proto',
  package='connectme',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0f\x63onnectme.proto\x12\tconnectme\"\x18\n\x08\x46ilePath\x12\x0c\n\x04path\x18\x01 \x01(\t\")\n\x0c\x46ileChecksum\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0b\n\x03sum\x18\x02 \x01(\t\"8\n\tFileChunk\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0f\n\x07\x63ounter\x18\x02 \x01(\x04\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"5\n\tPutReturn\x12\x13\n\x0btotal_files\x18\x01 \x01(\x04\x12\x13\n\x0btotal_bytes\x18\x02 \x01(\x04\"\x07\n\x05\x45mpty2\x84\x01\n\x0b\x46ileManager\x12>\n\x08\x43hecksum\x12\x13.connectme.FilePath\x1a\x17.connectme.FileChecksum\"\x00(\x01\x30\x01\x12\x35\n\x03Put\x12\x14.connectme.FileChunk\x1a\x14.connectme.PutReturn\"\x00(\x01\x62\x06proto3')
)




_FILEPATH = _descriptor.Descriptor(
  name='FilePath',
  full_name='connectme.FilePath',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='connectme.FilePath.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=54,
)


_FILECHECKSUM = _descriptor.Descriptor(
  name='FileChecksum',
  full_name='connectme.FileChecksum',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='connectme.FileChecksum.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sum', full_name='connectme.FileChecksum.sum', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=56,
  serialized_end=97,
)


_FILECHUNK = _descriptor.Descriptor(
  name='FileChunk',
  full_name='connectme.FileChunk',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='connectme.FileChunk.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='counter', full_name='connectme.FileChunk.counter', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='connectme.FileChunk.data', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=99,
  serialized_end=155,
)


_PUTRETURN = _descriptor.Descriptor(
  name='PutReturn',
  full_name='connectme.PutReturn',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='total_files', full_name='connectme.PutReturn.total_files', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_bytes', full_name='connectme.PutReturn.total_bytes', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=157,
  serialized_end=210,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='connectme.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=212,
  serialized_end=219,
)

DESCRIPTOR.message_types_by_name['FilePath'] = _FILEPATH
DESCRIPTOR.message_types_by_name['FileChecksum'] = _FILECHECKSUM
DESCRIPTOR.message_types_by_name['FileChunk'] = _FILECHUNK
DESCRIPTOR.message_types_by_name['PutReturn'] = _PUTRETURN
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FilePath = _reflection.GeneratedProtocolMessageType('FilePath', (_message.Message,), dict(
  DESCRIPTOR = _FILEPATH,
  __module__ = 'connectme_pb2'
  # @@protoc_insertion_point(class_scope:connectme.FilePath)
  ))
_sym_db.RegisterMessage(FilePath)

FileChecksum = _reflection.GeneratedProtocolMessageType('FileChecksum', (_message.Message,), dict(
  DESCRIPTOR = _FILECHECKSUM,
  __module__ = 'connectme_pb2'
  # @@protoc_insertion_point(class_scope:connectme.FileChecksum)
  ))
_sym_db.RegisterMessage(FileChecksum)

FileChunk = _reflection.GeneratedProtocolMessageType('FileChunk', (_message.Message,), dict(
  DESCRIPTOR = _FILECHUNK,
  __module__ = 'connectme_pb2'
  # @@protoc_insertion_point(class_scope:connectme.FileChunk)
  ))
_sym_db.RegisterMessage(FileChunk)

PutReturn = _reflection.GeneratedProtocolMessageType('PutReturn', (_message.Message,), dict(
  DESCRIPTOR = _PUTRETURN,
  __module__ = 'connectme_pb2'
  # @@protoc_insertion_point(class_scope:connectme.PutReturn)
  ))
_sym_db.RegisterMessage(PutReturn)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), dict(
  DESCRIPTOR = _EMPTY,
  __module__ = 'connectme_pb2'
  # @@protoc_insertion_point(class_scope:connectme.Empty)
  ))
_sym_db.RegisterMessage(Empty)



_FILEMANAGER = _descriptor.ServiceDescriptor(
  name='FileManager',
  full_name='connectme.FileManager',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=222,
  serialized_end=354,
  methods=[
  _descriptor.MethodDescriptor(
    name='Checksum',
    full_name='connectme.FileManager.Checksum',
    index=0,
    containing_service=None,
    input_type=_FILEPATH,
    output_type=_FILECHECKSUM,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Put',
    full_name='connectme.FileManager.Put',
    index=1,
    containing_service=None,
    input_type=_FILECHUNK,
    output_type=_PUTRETURN,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_FILEMANAGER)

DESCRIPTOR.services_by_name['FileManager'] = _FILEMANAGER

# @@protoc_insertion_point(module_scope)
