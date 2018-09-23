#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep


cnt = 0
oldcnt = 0
t = 0

def callback(arg):
    global cnt
    cnt+=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.output(18, GPIO.HIGH)
GPIO.add_event_detect(18, GPIO.RISING)
GPIO.add_event_callback(18, callback)

while True:
    t = cnt
    hz = t - oldcnt

    print("FREQ: " + str(hz) + "\t = " + str((hz+50)/100) + " mW/m2")
    oldcnt = t

    #print(str(GPIO.input(18)))
    sleep(1)
