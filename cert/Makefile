# Craig Hesling
# Oct 8, 2018

.PHONY: all ca server client clean

all: ca server client

ca: ca.key ca.pem
server: server.key server.crt
client: client.key client.crt

%.key:
	openssl genrsa -out $@ 2048

# Generating CA certs
ca.pem: ca.key
	openssl req -new -x509 -nodes -key $< -sha256 -out $@

# For certs that will be signed by the CA
%.csr: %.key
	openssl req -new -key $< -out $@
%.crt: %.csr ca.key ca.key
	openssl x509 -req -in $< -CA ca.pem -CAkey ca.key -CAcreateserial -out $*.crt -days 1825 -sha256

# Example usage: FILE=client.crt make inspect-pem
inspect-pem:
	openssl x509 -text -in $(FILE)
inspect-key:
	openssl rsa -text -in $(FILE)
checkserver:
	openssl s_client -connect localhost:50051

clean:
	$(RM) *.key *.pem *.crt *.srl
