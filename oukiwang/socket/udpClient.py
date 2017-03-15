import socket
port=10086
host='192.168.1.66'
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.sendto(b'hello',(host,port))