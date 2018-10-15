import hashlib
import glob
from logging import Logger

import grpc

import connectme_pb2
import connectme_pb2_grpc

class ConnectMe:
    VERSION_MAJOR          = 1
    VERSION_MINOR          = 0

    DEFAULT_SERVER_ADDRESS = "[::]:50051"
    DEFAULT_CLIENT_ADDRESS = "localhost:50051"

    DEFAULT_ROOT_CERT_FILE = 'cert/ca.pem'
    DEFAULT_SERVER_KEY_FILE = 'cert/server.key'
    DEFAULT_SERVER_CHAIN_FILE = 'cert/server.crt'
    DEFAULT_CLIENT_KEY_FILE = 'cert/client.key'
    DEFAULT_CLIENT_CHAIN_FILE = 'cert/client.crt'

    def __init__(self, address: str):
        # We should ask the local FS what the block size is
        self.local_block_size = 65536
        # self.local_block_size = 1
        self.address: str = address

    def expandPath(self, path: str):
        return glob.glob(path)

    def sha256file(self, path: str):
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while True:
                data = f.read(self.local_block_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def fileChunkGenerator(self, paths, prefix: str):
        """
        Path names are in terms of the remote server path
        """
        for path in paths:
            counter: int = 0
            with open(path, 'rb') as f:
                # Read chunks and send
                while True:
                    data = f.read(self.local_block_size)
                    if not data:
                        break
                    yield connectme_pb2.FileChunk(path=prefix+path, counter=counter, data=data)
                    counter += 1
    def FormatVersion(self, ver: tuple):
        (major,minor) = ver
        return '{}.{}'.format(major, minor)