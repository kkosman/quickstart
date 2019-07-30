#!/usr/bin/env python2.7


import datetime
import serial


ser = serial.Serial(
  
   port='/dev/ttyUSB0',
   baudrate = 9600,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
)
counter=0


while 1:
   x=ser.readline()
   if len(x) > 0:
       date = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " => "
       print(date + x)
       with open('logs/sensor.log', 'a') as f:
               f.write(date + x)
