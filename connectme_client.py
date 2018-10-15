#!/usr/bin/env python3
# Craig Hesling
# Oct 7, 2018

import logging
import os
import sys
import select
from queue import Queue
from threading import Thread, Event
import select

import grpc

import connectme_pb2
import connectme_pb2_grpc
from connectme_common import *


class ConnectMeClient(ConnectMe):
    def __init__(self, address=ConnectMe.DEFAULT_CLIENT_ADDRESS):
        super(ConnectMeClient, self).__init__(address)

    def _setup(self):
        self.filemanager = connectme_pb2_grpc.FileManagerStub(self.channel)
        self.metamanager = connectme_pb2_grpc.MetaManagerStub(self.channel)
        self.consolemanager = connectme_pb2_grpc.ConsoleManagerStub(self.channel)

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
                # pass any other gRPC errors to user
                raise e

    def FilePut(self, source_paths: list, remote_destination: str):
        """
        Transfers the files listed in source_paths to the remote directory remote_destination
        This function can throw FileNotFoundError.
        """
        lastChar = remote_destination[len(remote_destination)-1]
        if lastChar != '/':
            remote_destination += '/'

        try:
            paths = [p for pat in source_paths for p in self.expandPath(pat)]
            g = self.fileChunkGenerator(paths, True, remote_destination)
            status = self.filemanager.Put(g)
            print('# Copied {} files'.format(status.total_files))
            print('# Copied {} bytes'.format(status.total_bytes))
        except grpc.RpcError as e:
            status_code = e.code()  # status_code.name and status_code.value
            if grpc.StatusCode.NOT_FOUND == status_code:
                raise FileNotFoundError(e.details()) from e
            else:
                # pass any other gRPC errors to user
                raise e

    def FileGet(self, remote_paths: list, local_destination: str):
        """
        Transfers the files listed in remote_paths to the local directory local_destination
        This function can throw FileNotFoundError.
        """
        lastChar = local_destination[len(local_destination)-1]
        if lastChar != '/':
            local_destination += '/'

        try:
            filegen = (connectme_pb2.FilePath(path=p) for p in remote_paths)
            chunks = self.filemanager.Get(filegen)
            self.fileChunkReceiver(chunks, True, local_destination)
        except grpc.RpcError as e:
            status_code = e.code()  # status_code.name and status_code.value
            if grpc.StatusCode.NOT_FOUND == status_code:
                raise FileNotFoundError(e.details()) from e
            else:
                # pass any other gRPC errors to user
                raise e

    def ClientVersion(self):
            return (self.VERSION_MAJOR, self.VERSION_MINOR)

    def RemoteVersion(self):
        try:
            ver = self.metamanager.Version(connectme_pb2.VersionRequest())
            return (ver.major, ver.minor)
        except grpc.RpcError as e:
            status_code = e.code()  # status_code.name and status_code.value
            if grpc.StatusCode.NOT_FOUND == status_code:
                raise FileNotFoundError(e.details()) from e
            else:
                # pass any other gRPC errors to user
                raise e

    def _ioCollector(self, shutdown: Event, queue: Queue):
        """Read stdin and transfer as ConnectData messages to queue"""
        fd = os.dup(sys.stdin.fileno())
        sys.stdin.close()
        poller = select.poll()
        poller.register(fd, select.POLLIN)
        while True:
            # be 50ms responsive
            event = poller.poll(50)
            if shutdown.is_set():
                break
            if len(event) == 0:
                continue
            d = os.read(fd, self.local_block_size)
            if len(d) == 0:
                # EOF condition
                queue.put(connectme_pb2.ConnectData(ctrl=connectme_pb2.EOF))
                logging.debug('closing stdin io collector')
                break
            queue.put(connectme_pb2.ConnectData(data=d, channel=connectme_pb2.STDIN))

    def Launch(self, cmd: str, args: list = []):
        """Connect the local terminal to a remote command launch"""
        exitcode: int
        q = Queue()
        shutdown = Event()
        worker_stdin = Thread(target=self._ioCollector, args=(shutdown, q))
        worker_stdin.start()

        self.consolemanager.Launch(connectme_pb2.LaunchRequest(willconnect=True, command=cmd, arguments=args))
        for out in self.consolemanager.Connect(iter(q.get, None)):
            assert out.channel in [connectme_pb2.NOSTREAM, connectme_pb2.STDOUT, connectme_pb2.STDERR]
            if out.ctrl == connectme_pb2.EXIT:
                logging.debug('Received exitcode')
                q.put(None)
                shutdown.set()
                exitcode = out.exitcode
            if out.channel == connectme_pb2.STDOUT:
                if out.ctrl == connectme_pb2.EOF:
                    logging.debug('Closing stdout')
                    sys.stdout.flush()
                    # sys.stdout.close()
                else:
                    os.write(sys.stdout.fileno(), out.data)
            elif out.channel == connectme_pb2.STDERR:
                if out.ctrl == connectme_pb2.EOF:
                    logging.debug('Closing stderr')
                    sys.stderr.flush()
                    # sys.stderr.close()
                else:
                    os.write(sys.stderr.fileno(), out.data)
            # if sys.stdout.closed and sys.stderr.closed:
            #     return

        # sys.stdin.close()
        # os.close(sys.stdin.fileno())
        logging.debug('Launch finished')
        return exitcode