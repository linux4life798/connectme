import glob
import hashlib
import logging
import os
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
        """Use linux globs to expand a file pattern"""
        return glob.glob(path)

    def sha256file(self, path: str):
        """Generate sha256 for the given file path"""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while True:
                data = f.read(self.local_block_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def fileChunkGenerator(self, paths, strippath: bool, prefix: str=''):
        """Path names are in terms of the remote server path"""
        for path in paths:
            counter: int = 0
            with open(path, 'rb') as f:
                dstpath: str
                if strippath:
                    dstpath = prefix+os.path.basename(path)
                else:
                    dstpath = prefix+path
                # Read chunks and send
                logging.debug('Generating chunks for %s -> %s' % (path,dstpath))
                while True:
                    data = f.read(self.local_block_size)
                    if not data:
                        break
                    yield connectme_pb2.FileChunk(path=dstpath, counter=counter, data=data)
                    counter += 1

    def fileChunkReceiver(self, chunk_iter, strippath: bool, prefix: str=''):
        total_files: int = 0
        total_bytes: int = 0
        path: str = "/dev/null"
        file = open(path, "wb")
        for chunk in chunk_iter:
            if chunk.counter == 0:
                file.close()
                dstpath: str
                if strippath:
                    dstpath = prefix+os.path.basename(chunk.path)
                else:
                    dstpath = prefix+chunk.path
                logging.debug('Receiving chunks for %s -> %s' % (chunk.path,dstpath))
                file = open(dstpath, "wb")
                total_files += 1
            file.write(chunk.data)
            total_bytes += len(chunk.data)
        file.close()
        return (total_files, total_bytes)

    def fileChunkChecksummer(self, chunk_iter):
        """
        Calculate checksums for files given as chunks
        Returns as FileChecksum object
        """
        firstfile = True
        sha256: hashlib.sha256 = hashlib.sha256()
        for chunk in chunk_iter:
            if chunk.counter == 0:
                if firstfile:
                    firstfile = False
                else:
                    yield connectme_pb2.FileChecksum(path=chunk.path, sum=sha256.hexdigest())
                logging.debug('Receiving chunks for %s' % chunk.path)
                sha256 = hashlib.sha256()
            sha256.update(chunk.data)
        # write out last file checksum
        yield connectme_pb2.FileChecksum(path=chunk.path, sum=sha256.hexdigest())

    def FormatVersion(self, ver: tuple):
        """Return the human readable string composed of the major and minor version"""
        (major,minor) = ver
        return '{}.{}'.format(major, minor)
