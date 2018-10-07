#!/usr/bin/env python3

import os
import argparse
import concurrent.futures as futures
import hashlib
import time

import grpc

import connectme_pb2
import connectme_pb2_grpc


DEFAULT_SERVER_ADDRESS = "[::]:50051"
DEFAULT_CLIENT_ADDRESS = "localhost:50051"

# Things I Want To Ensure Correctness On
# * Byte order correction
# * Timeout for running remote commands (maybe sigstop and ask client what to do)
# * SSL


class ConnectMe:
    def __init__(self, address):
        # We should ask the local FS what the block size is
        self.local_block_size = 65536
        self.address = address

    def sha256file(self, path):
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while True:
                data = f.read(self.local_block_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def fileChunkGenerator(self, paths: list, prefix: str):
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
                    # print(type(path))
                    # print(type(prefix))
                    # print(type(prefix+path))
                    yield connectme_pb2.FileChunk(path=prefix+path, counter=counter, data=data)
                    counter += 1


class ConnectMeServer(ConnectMe, connectme_pb2_grpc.FileManagerServicer):
    def __init__(self, address=DEFAULT_SERVER_ADDRESS):
        super(ConnectMeServer, self).__init__(address)

    def Checksum(self, request_iterator: connectme_pb2.FilePath, context: grpc.ServicerContext):
        """
        """
        for file in request_iterator:
            sha256: str
            try:
                sha256 = self.sha256file(file.path)
            except FileNotFoundError:
                print('Failed to find {}'.format(file.path))
                details = "File \"{}\" does not exist".format(file.path)
                context.abort(grpc.StatusCode.NOT_FOUND, details)
            yield connectme_pb2.FileChecksum(path=file.path, sum=sha256)

    def Put(self, request_iterator: connectme_pb2.FileChunk, context: grpc.ServicerContext):
        total_files: int = 0
        total_bytes: int = 0

        path: str = "/dev/null"
        file = open(path, "wb")
        for chunk in request_iterator:
            if chunk.counter == 0:
                file.close()
                path = chunk.path
                file = open(path, "xb")
                total_files += 1
            file.write(chunk.data)
            total_bytes += len(chunk.data)

            # try:
            #     pass
            # except FileNotFoundError:
            #     print('Failed to find {}'.format(file.path))
            #     details = "File \"{}\" does not exist".format(file.path)
            #     context.abort(grpc.StatusCode.NOT_FOUND, details)
        file.close()
        return connectme_pb2.PutReturn(total_files=total_files, total_bytes=total_bytes)

    def Start(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        connectme_pb2_grpc.add_FileManagerServicer_to_server(
            ConnectMeServer(), self.server)
        # self.server.add_insecure_port('[::]:50051')
        self.server.add_insecure_port(self.address)
        self.server.start()

    def Stop(self):
        self.server.stop(0)


class ConnectMeClient(ConnectMe):
    def __init__(self, address=DEFAULT_CLIENT_ADDRESS):
        super(ConnectMeClient, self).__init__(address)

    def Connect(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.filemanager = connectme_pb2_grpc.FileManagerStub(self.channel)

    def FileRemoteChecksum(self, paths: list):
        """
        Retrieves the checksum of the remote file paths listed in the paths list
        This function can throw FileNotFoundError.
        """
        try:
            g = (connectme_pb2.FilePath(path=p) for p in paths)
            return [c.sum for c in self.filemanager.Checksum(g)]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="the server address to bind or connect to",
                        nargs="?", default="localhost:50051")
    # parser.add_argument("-v", "--verbosity", type=int, help="increase output verbosity")
    parser.add_argument(
        "-s", "--server", help="indicate this is the server", action="store_true")
    subparsers = parser.add_subparsers(dest='command')
    parser_checksum = subparsers.add_parser(
        'checksum', help='Request the checksum of remote files')
    parser_checksum.add_argument(
        'file', nargs="+", type=str, help='A file path we wish to checksum')
    parser_put = subparsers.add_parser(
        'put', help='Transfer local files to remote server')
    parser_put.add_argument('source_file', nargs="+",
                            type=str, help='The path of files to send')
    parser_put.add_argument('remote_destination', type=str,
                            help='The remote path where we will deposit the files')
    args = parser.parse_args()

    if args.server:
        server: ConnectMeServer
        if args.address is not None:
            print('Running as server on', args.address)
            server = ConnectMeServer(args.address)
        else:
            print('Running as server')
            server = ConnectMeServer()

        try:
            server.Start()
        except grpc.RpcError as e:
            print('Failed to start server: ', e)
            exit(1)

        # Wait for keyboard interrupt to shutdown server
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Shutting down server')
            server.Stop()
    else:
        client: ConnectMeClient
        if args.address is not None:
            print('Running as client to ', args.address)
            client = ConnectMeClient(args.address)
        else:
            print('Running as client with default address')
            client = ConnectMeClient()

        client.Connect()

        if args.command == "checksum":
            print('files = ', args.file)
            try:
                checksum = client.FileRemoteChecksum(args.file)
            except FileNotFoundError as e:
                print('File not found: ', e)
            else:
                # Output the sum and file in standard checksum format
                for (f, sum) in zip(args.file, checksum):
                    print(sum, f)
        elif args.command == "put":
            print('source_file = ', args.source_file)
            print('remote_destination = ', args.remote_destination)
            try:
                checksum = client.FilePut(
                    args.source_file, args.remote_destination)
            except FileNotFoundError as e:
                print('File not found: ', e)
            # else:
            #     # Output the sum and file in standard checksum format
            #     for (f, sum) in zip(args.file, checksum):
            #         print(sum, f)
