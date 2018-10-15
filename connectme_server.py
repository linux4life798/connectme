#!/usr/bin/env python3
# Craig Hesling
# Oct 7, 2018

import concurrent.futures as futures
import glob
import logging
import os
import signal
import subprocess
import time
from queue import Queue
from threading import Thread

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
        """Fetch the sha256 checksum for the incoming file patterns"""
        for file in request_iterator:
            paths = self.expandPath(file.path)
            if len(paths) == 0:
                details = "File \"{}\" does not exist".format(file.path)
                logging.warn(details)
                context.abort(grpc.StatusCode.NOT_FOUND, details)
            for path in paths:
                sum: str
                try:
                    logging.debug("expanded paths = {}".format(path))
                    sum = self.sha256file(path)
                except FileNotFoundError:
                    logging.warn('Failed to find {}'.format(path))
                    details = "File \"{}\" does not exist".format(path)
                    context.abort(grpc.StatusCode.NOT_FOUND, details)
                except Exception as e:
                    details = "Unknown error on open or read: \"{}\"".format(e)
                    context.abort(grpc.StatusCode.UNKNOWN, details)
                yield connectme_pb2.FileChecksum(path=path, sum=sum)

    def Put(self, request_iterator: connectme_pb2.FileChunk, context: grpc.ServicerContext):
        """Write/create the incoming files"""
        total_files: int = 0
        total_bytes: int = 0
        try:
            # paths are with respect to server side fs
            (total_files, total_bytes) = self.fileChunkReceiver(request_iterator, False)
        except IsADirectoryError as e:
            details = "Tried to write to directory: \"{}\"".format(e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, details)
        except Exception as e:
            details = "Unknown error on open or write: \"{}\"".format(e)
            context.abort(grpc.StatusCode.UNKNOWN, details)
        return connectme_pb2.PutReturn(total_files=total_files, total_bytes=total_bytes)

    def Get(self, request_iterator: connectme_pb2.FilePath, context: grpc.ServicerContext):
        """Fetch the incoming file patterns"""
        for file in request_iterator:
            try:
                # paths are with respect to server side fs
                paths = self.expandPath(file.path)
                if len(paths) == 0:
                    raise FileNotFoundError(file.path)
                for c in self.fileChunkGenerator(paths, False):
                    yield c
            except FileNotFoundError as e:
                details = "File not found: \"{}\"".format(e)
                logging.warn(details)
                context.abort(grpc.StatusCode.NOT_FOUND, details)
            except Exception as e:
                details = "Unknown error on open or read: \"{}\"".format(e)
                context.abort(grpc.StatusCode.UNKNOWN, details)


    def Version(self, req: connectme_pb2.VersionRequest, context: grpc.ServicerContext):
        """Fetch the server library major/minor version"""
        return connectme_pb2.VersionResponse(major=self.VERSION_MAJOR, minor=self.VERSION_MINOR)

    def Launch(self, req: connectme_pb2.LaunchRequest, contex: grpc.RpcContext):
        logging.debug('Launch cmd={} args={}'.format(req.command, req.arguments))
        args = [ req.command ]
        for a in req.arguments:
            args.append(a)
        if req.willconnect:
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.proc = subprocess.Popen(args)
        return connectme_pb2.LaunchResponse()

    def _ioCollector(self, queue: Queue, reader, chtype: connectme_pb2.DataStream):
        while True:
            d = bytes(reader.readline(self.local_block_size))
            if len(d) == 0:
                queue.put(connectme_pb2.ConnectData(channel=chtype, ctrl=connectme_pb2.EOF))
                queue.put(None)
                logging.info('closing {}'.format(str(chtype)))
                return
            queue.put(connectme_pb2.ConnectData(data=d, channel=chtype, ctrl=connectme_pb2.NOSIG))

    def _ioTransmitter(self, req_iter):
        for input in req_iter:
            input: connectme_pb2.ConnectData
            assert input.channel in [connectme_pb2.NOSTREAM, connectme_pb2.STDIN]
            # write out bytes to stdin
            self.proc.stdin.write(input.data)
            self.proc.stdin.flush()
            # send ctrl signals
            if input.ctrl != connectme_pb2.NOSIG:
                if input.ctrl == connectme_pb2.EOF:
                    self.proc.stdin.close()
                elif input.ctrl == connectme_pb2.SIGINT:
                    logging.debug('sending SIGINT')
                    self.proc.send_signal(int(signal.SIGINT))
                elif input.ctrl==connectme_pb2.SIGKILL:
                    logging.debug('sending SIGKILL')
                    self.proc.send_signal(int(signal.SIGKILL))
        logging.debug('closing io transmitter')

    def Connect(self, req_iter: connectme_pb2.ConnectData, contex: grpc.RpcContext):
        q = Queue(1)
        worker_stdout = Thread(target=self._ioCollector, args=(q, self.proc.stdout, connectme_pb2.STDOUT))
        worker_stdout.start()
        worker_stderr = Thread(target=self._ioCollector, args=(q, self.proc.stderr, connectme_pb2.STDERR))
        worker_stderr.start()
        worker_stdin = Thread(target=self._ioTransmitter, args=(req_iter,))
        worker_stdin.start()
        # run loop for outgoing data
        nonecount = 0
        while True:
            d = q.get()
            if d == None:
                nonecount += 1
                if nonecount == 2:
                    logging.debug('Waiting for proc')
                    exitcode = self.proc.wait()
                    logging.debug('exitcode = {}'.format(exitcode))
                    yield connectme_pb2.ConnectData(channel=connectme_pb2.NOSTREAM, ctrl=connectme_pb2.EXIT, exitcode=exitcode)
                    logging.info('Connect closed')
                    return
            else:
                yield d

    def _setup(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        connectme_pb2_grpc.add_FileManagerServicer_to_server(self, self.server)
        connectme_pb2_grpc.add_MetaManagerServicer_to_server(self, self.server)
        connectme_pb2_grpc.add_ConsoleManagerServicer_to_server(self, self.server)

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
