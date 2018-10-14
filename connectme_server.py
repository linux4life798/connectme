#!/usr/bin/env python3
# Craig Hesling
# Oct 7, 2018

import concurrent.futures as futures
import os
import time
import glob

import grpc

import connectme_pb2
import connectme_pb2_grpc
from connectme_common import *

# Things I Want To Ensure Correctness On
# * Byte order correction
# * Timeout for running remote commands (maybe sigstop and ask client what to do)
# * SSL

# Write a pair of python scripts to communicate and perform a small set of actions between two machines. Use sockets for the communication mechanism. Implement the following commands.
# Execute shell command on server
# Transfer file to server
# Retrieve file from server
# Retrieve server version info
# Send a chunk of data, which the server will calculate a checksum and return the checksum (crc32, sha256, your choice)


class ConnectMeServer(ConnectMe, connectme_pb2_grpc.FileManagerServicer):
    def __init__(self, address=ConnectMe.DEFAULT_SERVER_ADDRESS):
        super(ConnectMeServer, self).__init__(address)

    def Checksum(self, request_iterator: connectme_pb2.FilePath, context: grpc.ServicerContext):
        """
        """
        for file in request_iterator:
            for path in self.expandPath(file.path):
                sha256: str
                try:
                    print("expanded paths = ", path)
                    sha256 = self.sha256file(path)
                except FileNotFoundError:
                    print('Failed to find {}'.format(path))
                    details = "File \"{}\" does not exist".format(path)
                    context.abort(grpc.StatusCode.NOT_FOUND, details)
                yield connectme_pb2.FileChecksum(path=path, sum=sha256)

    def Put(self, request_iterator: connectme_pb2.FileChunk, context: grpc.ServicerContext):
        total_files: int = 0
        total_bytes: int = 0

        path: str = "/dev/null"
        file = open(path, "wb")
        for chunk in request_iterator:
            if chunk.counter == 0:
                file.close()
                path = chunk.path
                file = open(path, "wb")
                total_files += 1
            file.write(chunk.data)
            total_bytes += len(chunk.data)
        file.close()
        return connectme_pb2.PutReturn(total_files=total_files, total_bytes=total_bytes)

    def Get(self, request_iterator: connectme_pb2.FilePath, context: grpc.ServicerContext):
        """
        """
        for file in request_iterator:
            try:
                sha256 = self.sha256file(file.path)
            except FileNotFoundError:
                print('Failed to find {}'.format(file.path))
                details = "File \"{}\" does not exist".format(file.path)
                context.abort(grpc.StatusCode.NOT_FOUND, details)
            yield connectme_pb2.FileChecksum(path=file.path, sum=sha256)

    def _setup(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        connectme_pb2_grpc.add_FileManagerServicer_to_server(self, self.server)

    def Start(self):
        self._setup()
        self.server.add_insecure_port(self.address)
        self.server.start()

    def StartSSL(self):
        self._setup()
        with open(self.DEFAULT_SERVER_KEY_FILE, 'rb') as f:
            private_key = f.read()
        with open(self.DEFAULT_SERVER_CHAIN_FILE, 'rb') as f:
            certificate_chain = f.read()
        with open(self.DEFAULT_ROOT_CERT_FILE, 'rb') as f:
            root_ca = f.read()
        # This credentials line requires client's ssl certs to have been signed by the specifies CA
        server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain,),), root_certificates=root_ca, require_client_auth=True)
        self.server.add_secure_port(self.address, server_credentials)
        self.server.start()

    def Stop(self):
        self.server.stop(0)
