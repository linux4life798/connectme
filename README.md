# ConnectMe

# Exmple usage
```bash
./connectme.py - launch -- ls -al
```

# Features
* TLS/SSL enabled with mutual authentication
* Remote file glob evaluation

# Anti-Features
* Cannot recursively copy directories and files
* Ony uses SHA256

# Prerequisites

## Python gRPC Library
```bash
pip3 install grpcio-tools googleapis-common-protos
```

## CA, Server, and Client SSL Certificates
```bash
make sslcerts
```
