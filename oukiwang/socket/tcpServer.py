import network
import socket
import time

wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
wlan.connect('rd','hidfrobot5353')
while(wlan.isconnected() is False):
    time.sleep(1)
ip=wlan.ifconfig()[0]
listenSocket = socket.socket()
listenSocket.bind((ip,10086))
listenSocket.listen(1)
listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print ('tcp waiting...')
try:
  while True:
    print("accepting.....")
    conn,addr = listenSocket.accept()
    print(addr,"connected")

    while True:
        data = conn.recv(1024)
        if(len(data) == 0):
            print("close socket")
            conn.close()
            break
        print(data)
        ret = conn.send(data)
except:
    listenSocket.close()
