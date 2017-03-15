# -*- coding: utf-8 -*-

import os
import sys
import serial
import struct  
import time
import hashlib
import threading
import serial
import serial.tools.list_ports

from PyQt4 import QtGui,QtCore

startUpgradeMutex=threading.Lock()
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
fileName=None
uartName=None
baudRate=None
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

class UI(QtGui.QWidget):
    def __init__(self):
        super(UI,self).__init__()
        self.initUI()
    def initUI(self):
        self.resize(400,200)
        self.move(300,300)
        self.comLabel=QtGui.QLabel("Com Port",self)
        self.comLabel.move(40,80)
        self.baudLabel=QtGui.QLabel("Baud Rate",self)
        self.baudLabel.move(260,80)
        
        self.setWindowTitle('Simple')
        self.openBtn=QtGui.QPushButton('Open',self)
        self.openBtn.move(40,130)
        self.openBtn.resize(58,23)
        self.openBtn.clicked.connect(self.showDialog)
        self.burnBtn=QtGui.QPushButton('Burn',self)
        self.burnBtn.resize(58,23)
        self.burnBtn.clicked.connect(self.burnFirmware)
        self.burnBtn.move(340,130)
        self.le=QtGui.QLineEdit(self)
        self.le.move(110,130)
        self.le.resize(100,23)
        self.lcd=QtGui.QLCDNumber(self)
        self.lcd.move(220,130)
        self.lcd.resize(120,60)
        self.lcd.display(50)
        self.baudComboBox=QtGui.QComboBox(self)
        self.baudComboBox.move(260,100)
        self.baudComboBox.addItem("115200")
        self.baudComboBox.addItem("256000")
        self.uartComboBox=QtGui.QComboBox(self)
        self.uartComboBox.move(40,100)
        port_list = list(serial.tools.list_ports.comports())
        for x in port_list:
            self.uartComboBox.addItem(x[0])
        self.show()
    def showDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file','./','*.bin *.img')
        self.le.setText(str(fname))
    def burnFirmware(self):
        global uartName,baudRate,fileName
        if not os.path.isfile(self.le.text()):
            QtGui.QMessageBox.information(self,"Error", "file not exist",QtGui.QMessageBox.Yes)
            return
        uartName=self.uartComboBox.currentText()
        baudRate=self.baudComboBox.currentText()
        fileName=self.le.text()
        self.burnBtn.setEnabled(False)
        startUpgradeMutex.release()

class UpgradeThread(threading.Thread,QtCore.QObject):
    percentSignal = QtCore.pyqtSignal(object)
    def __init__(self,ui):
        super(UpgradeThread,self).__init__()
        super(QtCore.QObject,self).__init__()
        self.ui = ui
    def run(self):
        startUpgradeMutex.acquire()  
        print      fileName
        print      uartName
        print      baudRate
        flush()
        f = open(fileName, 'rb')
        sh = hashlib.sha256()
        sh.update(f.read())
        newVersion = f.name[str(f.name).find(".img")-3:str(f.name).find(".img")]
        f.close()
        sha256="".join('{:02x}'.format(ord(x)) for x in sh.digest())
        print sha256
        flush()
        oldVersion=getFwVersion()
        print "old=%s new=%s"%(oldVersion,newVersion)
        flush()
        print("------startUpgrade---------")
        flush()
        startUpgrade()
        print("------sendFile---------")
        flush()
        sendFile(fileName)
        print("------sendSha256---------")
        flush()
        sendSha256(sha256)
        print("------endUpgrade---------")
        flush()
        endUpgrade()
        print("------end---------")        

        self.percentSignal.emit(100)

    def percent(self,number):
        print("percent = %d"%(number))
        flush()

startUpgradeMutex.acquire()
app=QtGui.QApplication(sys.argv)
ui=UI()
upgrade=UpgradeThread(ui)
upgrade.start()
upgrade.percentSignal.connect(ui.lcd.display)

sys.exit(app.exec_())


f = open('./usb_cdc_V0.2.img', 'rb')
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
sendFile('../usb_cdc_V0.2.img')
sendSha256(sha256)
endUpgrade()
