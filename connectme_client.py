#!/usr/bin/env python3
# Craig Hesling
# Oct 7, 2018

import grpc

import connectme_pb2
import connectme_pb2_grpc
from connectme_common import *


class ConnectMeClient(ConnectMe):
    def __init__(self, address=ConnectMe.DEFAULT_CLIENT_ADDRESS):
        super(ConnectMeClient, self).__init__(address)

    def _setup(self):
        self.filemanager = connectme_pb2_grpc.FileManagerStub(self.channel)
        self.filemanager = connectme_pb2_grpc.MetaStub(self.channel)
        self.filemanager = connectme_pb2_grpc.ConsoleStub(self.channel)

    def Connect(self):
        self.channel = grpc.insecure_channel(self.address)
        self._setup()
    def ConnectSSL(self):
        with open(self.DEFAULT_CLIENT_KEY_FILE, 'rb') as f:
            private_key = f.read()
        with open(self.DEFAULT_CLIENT_CHAIN_FILE, 'rb') as f:
            certificate_chain = f.read()
        with open(self.DEFAULT_ROOT_CERT_FILE, 'rb') as f:
            root_ca = f.read()
        credentials = grpc.ssl_channel_credentials(root_certificates=root_ca, private_key=private_key, certificate_chain=certificate_chain)
        self.channel = grpc.secure_channel(self.address, credentials)
        self._setup()

    def FileRemoteChecksum(self, paths: list):
        """
        Retrieves the checksum of the remote file paths listed in the paths list
        This function can throw FileNotFoundError.
        """
        try:
            g = (connectme_pb2.FilePath(path=p) for p in paths)
            return {c.path: c.sum for c in self.filemanager.Checksum(g)}
        except grpc.RpcError as e:
            status_code = e.code()  # status_code.name and status_code.value
            if grpc.StatusCode.NOT_FOUND == status_code:
                raise FileNotFoundError(e.details()) from e
            else:
                # pass any other gRPC erros to user
                raise e

    def FilePut(self, source_paths: list, remote_destination: str):
        """
        Transfers the files listed in source_paths to the remote directory remote_destination
        This function can throw FileNotFoundError.
        """

        try:
            lastChar = remote_destination[len(remote_destination)-1]
            if lastChar != '/':
                remote_destination += '/'
            g = self.fileChunkGenerator(source_paths, remote_destination)
            status = self.filemanager.Put(g)
            print('# Copied {} files'.format(status.total_files))
            print('# Copied {} bytes'.format(status.total_bytes))
        except grpc.RpcError as e:
            status_code = e.code()  # status_code.name and status_code.value
            if grpc.StatusCode.NOT_FOUND == status_code:
                raise FileNotFoundError(e.details()) from e
            else:
                # pass any other gRPC erros to user
                raise e

    def FileGet(self, remote_paths: list, local_destination: str):
        """
        Transfers the files listed in remote_paths to the local directory local_destination
        This function can throw FileNotFoundError.
        """
        raise NotImplementedError()

    def Launch(self, cmd: str, args: list = []):
        """
        Connect the local terminal to a remote command launch
        """
