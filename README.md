# ConnectMe

# Features
* TLS/SSL enabled with mutual authentication
* Remote file glob evaluation
* If connection drops during connect session, process will be killed

# Example usage

## Setup certs
```bash
make sslcerts
```

## Launch server
```bash
./connectme.py -v -s
```

## Remote launch command
```bash
./connectme.py - launch -- ls -al
```

## Put files
```bash
./connectme.py -v - put testdir/src/*.txt testdir/dest
```

## Get files
```bash
./connectme.py -v - get 'testdir/src/*.txt' testdir/dest
```

## Get file checksums
```bash
./connectme.py -v - checksum 'testdir/src*/*.txt'
```

# Anti-Features
* Cannot recursively copy directories and files
* Ony uses SHA256
* Can only handle one launch/connect at a time.
  Process races will occur if more than one are attempted.

# Prerequisites

## Python gRPC Library
```bash
pip3 install grpcio-tools googleapis-common-protos
```

## CA, Server, and Client SSL Certificates
```bash
make sslcerts
```
