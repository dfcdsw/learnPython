import sdcard,os
import socket
import ujson
import network
import time
import sys
from machine import Pin,SPI


def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    data = s.recv(512)
    s.close()
    return str(data,'utf8')

def connectWifi(ssid,passwd):
  wlan=network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.disconnect()
  wlan.connect(ssid,passwd)
  while(wlan.ifconfig()[0]=='0.0.0.0'):
    time.sleep(1)
  try:
    socket.getaddrinfo('dfrobot.com', 80)[0][4][0]
  except:
    print('can NOT connect to internet')
    return False
  return True


spi = SPI(baudrate=100000, polarity=1, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
sd = sdcard.SDCard(spi, Pin(16))
os.umount()
tmp=os.VfsFat(sd,"sd")

if(connectWifi('rd','hidfrobot5353') == True):
  s=http_get('http://202.58.105.240/test.json')
  s=s[s.find('\r\n\r\n')+4:]
  cfg=ujson.loads(s)
  f=open("config.json","rw+")
  f.write(ujson.dumps(cfg))
  f.close()
  print("get config file from internet")
else:
  f=open("config.json","r")
  cfg=ujson.loads(f.read())
  f.close()
  print("get config file from local file")
blinkInterval=cfg['blinkInterval']
print(cfg['name'])
led=Pin(cfg['led'],Pin.OUT)
relay=Pin(cfg['relay'],Pin.OUT)
relay.value(0)
while True:
  time.sleep(blinkInterval/1000)
  led.value(1)
  time.sleep(blinkInterval/1000)
  led.value(0)
