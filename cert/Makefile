# Craig Hesling
# Oct 8, 2018

COUNTRY = US
STATE   = Pennsylvania
CITY    = Pittsburgh
ORG     = ConnectMeCraigLTD
OU      = .
CN      = .

.PHONY: all ca server client clean
.PHONY: inspect-pem inspect-key checkserver

all: ca server client

ca: OU=CertAuthority
ca: ca.key ca.pem
server: OU=Server
server: CN=localhost
server: server.key server.crt
client: OU=Client
client: client.key client.crt

%.key:
	openssl genrsa -out $@ 2048

# Generating CA certs
ca.pem: ca.key
	openssl req -new -x509 -nodes -key $< -sha256 -out $@ -subj "/C=$(COUNTRY)/ST=$(STATE)/L=$(CITY)/O=$(ORG)/OU=$(OU)/CN=$(CN)"

# For certs that will be signed by the CA
%.csr: %.key
	openssl req -new -key $< -out $@ -subj "/C=$(COUNTRY)/ST=$(STATE)/L=$(CITY)/O=$(ORG)/OU=$(OU)/CN=$(CN)"
%.crt: %.csr ca.key ca.pem
	openssl x509 -req -in $< -CA ca.pem -CAkey ca.key -CAcreateserial -out $@  -sha256

# Example usage: FILE=client.crt make inspect-pem
inspect-pem:
	openssl x509 -text -in $(FILE)
inspect-key:
	openssl rsa -text -in $(FILE)
checkserver: ca.pem
	openssl s_client -verifyCAfile ca.pem -connect localhost:50051

clean:
	$(RM) *.key *.pem *.crt *.srl
