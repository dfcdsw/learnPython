#!/usr/bin/env python
# -*- coding: utf-8 -*
 
import serial
import serial.tools.list_ports
 
port_list = list(serial.tools.list_ports.comports())
for i in port_list:
    print i

