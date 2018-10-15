#!/usr/bin/env python3
# Craig Hesling
# Oct 7, 2018

import argparse
import logging
import sys
import time

import grpc

from connectme_client import *
from connectme_common import *
from connectme_server import *

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="the server address to bind or connect to", nargs="?", default="-")
    parser.add_argument("-s", "--server", help="indicate this is the server", action="store_true")
    parser.add_argument("-v", "--verbose", help="indicate if we should print more verbosely", action="store_true")
    parser.add_argument("-i", "--insecure", help="indicate if the connection should not use TLS/SSL", action="store_true")
    subparsers = parser.add_subparsers(dest='command')

    parser_checksum = subparsers.add_parser('checksum', help='Request the checksum of remote files')
    parser_checksum.add_argument('file', nargs="+", type=str, help='A file path we wish to checksum')

    parser_put = subparsers.add_parser('put', help='Transfer local files to remote server')
    parser_put.add_argument('local_file', nargs="+",type=str, help='The path of files to send')
    parser_put.add_argument('remote_destination', type=str, help='The remote path where we will deposit the files')

    parser_get = subparsers.add_parser('get', help='Transfer remote files to local client')
    parser_get.add_argument('remote_file', nargs="+", type=str, help='The path of the remote files')
    parser_get.add_argument('local_destination', type=str, help='The local directory to deposit the files')

    parser_version = subparsers.add_parser('version', help='Get version of client and remote server')

    parser_launch = subparsers.add_parser('launch', help='Launch a command on remote host')
    parser_launch.add_argument('cmd', type=str, help='The command path')
    parser_launch.add_argument('args', nargs="*", type=str, help='The command arguments')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)


    if args.server:
        server: ConnectMeServer
        if args.address == "-":
            args.address = ConnectMe.DEFAULT_SERVER_ADDRESS
        print('Running as server on', args.address, file=sys.stderr)
        server = ConnectMeServer(args.address)

        try:
            if args.insecure:
                server.Start()
            else:
                server.StartSSL()
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
        if args.address == "-":
            args.address = ConnectMe.DEFAULT_CLIENT_ADDRESS
        print('Running as client to', args.address, file=sys.stderr)
        client = ConnectMeClient(args.address)

        if args.insecure:
            client.Connect()
        else:
            client.ConnectSSL()

        if args.command == "checksum":
            logging.debug('files = %s' % args.file)
            try:
                checksums = client.FileRemoteChecksum(args.file)
            except FileNotFoundError as e:
                logging.error('File not found: %s' % e)
            else:
                # Output the sum and file in standard checksum format
                for f,sum in checksums.items():
                    print(sum, f)
        elif args.command == "put":
            logging.debug('local_file = %s' % args.local_file)
            logging.debug('remote_destination = %s' % args.remote_destination)
            try:
                client.FilePut(args.local_file, args.remote_destination)
            except FileNotFoundError as e:
                print('File not found: ', e)
        elif args.command == "get":
            logging.debug('remote_file = %s' % args.remote_file)
            logging.debug('local_destination = %s' % args.local_destination)
            try:
                client.FileGet(args.remote_file, args.local_destination)
            except FileNotFoundError as e:
                logging.error('File not found: %s' % e)
        elif args.command == "version":
            cver = client.ClientVersion()
            print('Client: %s' % client.FormatVersion(cver))
            rver = client.RemoteVersion()
            print('Remote: %s' % client.FormatVersion(rver))
            # To be compatible majors must match AND server must have at least client minor version
            if cver[0]!=rver[0] or cver[1]>rver[1]:
                print('Client may be incompatible with remote server')

        elif args.command == "launch":
            print('cmd = ', args.cmd, file=sys.stderr)
            print('args = ', args.args, file=sys.stderr)
            exitcode = client.Launch(args.cmd, args.args)
            sys.exit(exitcode)
