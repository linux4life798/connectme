# Craig Hesling <craig@hesling.com>

.PHONY: all clean

all: connectme_pb2_grpc.py connectme_pb2.py

connectme_pb2_grpc.py connectme_pb2.py: connectme.proto
	# Ensure you have done pip3 install grpcio-tools googleapis-common-protos
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $^

sslcerts:
	make -C cert/

clean:
	$(RM) connectme_pb2*
