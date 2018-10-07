# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import connectme_pb2 as connectme__pb2


class FileManagerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Checksum = channel.stream_stream(
        '/connectme.FileManager/Checksum',
        request_serializer=connectme__pb2.FilePath.SerializeToString,
        response_deserializer=connectme__pb2.FileChecksum.FromString,
        )
    self.Put = channel.stream_unary(
        '/connectme.FileManager/Put',
        request_serializer=connectme__pb2.FileChunk.SerializeToString,
        response_deserializer=connectme__pb2.PutReturn.FromString,
        )


class FileManagerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Checksum(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Put(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_FileManagerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Checksum': grpc.stream_stream_rpc_method_handler(
          servicer.Checksum,
          request_deserializer=connectme__pb2.FilePath.FromString,
          response_serializer=connectme__pb2.FileChecksum.SerializeToString,
      ),
      'Put': grpc.stream_unary_rpc_method_handler(
          servicer.Put,
          request_deserializer=connectme__pb2.FileChunk.FromString,
          response_serializer=connectme__pb2.PutReturn.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'connectme.FileManager', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
