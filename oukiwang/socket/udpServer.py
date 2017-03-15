import socket
import sys

port = 10086
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.1.66',port))
print('waiting....')
while True:
    data,addr=s.recvfrom(1024)
    print('received:',data,'from',addr)
    sys.stdout.flush()
