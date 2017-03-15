import os
import sys
import serial
import struct  
import time
import hashlib
from PyQt4 import QtGui,QtCore
sha256=0
com=serial.Serial('COM2')
#CMD
BOARD_FW_VERSION=1
OTA_FLASH_ADDR=2
START_UPGRADE=3
PACKET=4 #(OFFSET(32bit) DATA)
SEND_SHA256=5
END_UPGRADE=6
newVersion=0
oldVersion=0
#55 CS Length CMD ...
#55 CS Length CMD|0x80 01
#55 CS Length CMD|0x80 00
def flush():
    sys.stdout.flush()

def calcCs(data):
    cs=0
    if data is not None:
        for x in bytearray(data):
            cs+=x
    return cs

def analyzeRsp(cmd,rsp):
    (header,rspCs,length,rspCmd,rspData)=struct.unpack("=BBBB"+str(len(rsp)-4)+"s",rsp)
    print "%2X %2X %2X %2X %s"%(header,rspCs,length,rspCmd,rspData)
    print str(rspData)
    sys.stdout.flush()
    return True,rspData

def packAndSendPacket(cmd, data=None):
    length= 0
    if data is not None:
        length = len(bytearray(data))
    b=bytearray(struct.pack('=BBBB',0x55,0,length%255,cmd))
    if data is not None:
        for x in bytearray(data):
            b.append(x)
    b[1]=(calcCs(data)%256)
    com.write(b)
    com.flush()
    n=0
    while(n == 0):
        n=com.inWaiting()
        if(n==0):
            time.sleep(0.2)
    rsp=com.read(n)
    return analyzeRsp(cmd,rsp)
def sendFile(fileName):
    offset=0
    step=20480
    fp = open(fileName,'rb+')
    while True:
        fdata=bytearray(fp.read(step))
        if len(fdata) == 0:
            return True
        b=bytearray(struct.pack('=i',offset))+fdata
        packAndSendPacket(PACKET,b)
        offset+=step
    fp.close()
#pakcet 55(head) 00(cs) 00(len) 01(cmd)
#relay  55(head) 00(cs) 00(len) 81(cmd)
def getFwVersion():
    ret,relay=packAndSendPacket(BOARD_FW_VERSION)
    return relay

#55(head) AA(cs) 00(len) 02(cmd) 44 33 22 11(data)
def setFlashAddr():
    packAndSendPacket(OTA_FLASH_ADDR,bytearray('\x12\x23\x23\x64'))
    return True

def getFlashData():
    packAndSendPacket(OTA_FLASH_ADDR,bytearray('\x12\x23\x23\x64'))
    return True

def startUpgrade():
    packAndSendPacket(START_UPGRADE)
    return True

def sendSha256(sha):
    packAndSendPacket(SEND_SHA256,bytearray(sha))
    return True

def endUpgrade():
    packAndSendPacket(END_UPGRADE)
if not os.path.isfile('../usb_cdc.1.0.0.2.img'):
    exit()


def main():
    app=QtGui.QApplication(sys.argv)
    w=QtGui.QWidget()
    w.resize(250,150)
    w.move(300,300)
    w.setWindowTitle('Simple')
    w.show()
    sys.exit(app.exec_())
main()

f = open('../usb_cdc.1.0.0.2.img', 'rb')
sh = hashlib.sha256()
sh.update(f.read())
newVersion = f.name[f.name.find(".img")-3:f.name.find(".img")]
f.close()
sha256="".join('{:02x}'.format(ord(x)) for x in sh.digest())
flush()
oldVersion=getFwVersion()
print "old=%s new=%s"%(oldVersion,newVersion)
flush()
startUpgrade()
sendFile('../usb_cdc.1.0.0.2.img')
sendSha256(sha256)
endUpgrade()
