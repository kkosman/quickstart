#!/usr/bin/python3
# PIN 18

import sys
import time
from functools import reduce

mockup = False
try:
	import RPi.GPIO as GPIO
except:
    mockup = True
    print("No RPi, working with mockup Sensor")


class Sensor:
	global mockup
	__pin = 0
	instance = False

	cnt = 0
	oldcnt = 0
	t = 0
	array_hz = []

	def __init__(self, pin):
		self.__pin = pin
		if not mockup:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
			GPIO.add_event_detect(self.__pin, GPIO.RISING)
			GPIO.add_event_callback(self.__pin, self.callback)

	def callback(self, arg):
	    self.cnt += 1

	def measure(self):
		if mockup:
			return 65

		x = 0
		self.array_hz = []
		while x < 10:
			x += 1
			self.t = self.cnt
			hz = self.t - self.oldcnt

			print("FREQ: " + str(hz) + "\t = " + str((hz+50)/100) + " mW/m2")
			if x > 1:
				self.array_hz.append(hz)

			self.oldcnt = self.t
			time.sleep(1)
			
		if len(self.array_hz) > 1:
			value = reduce(lambda x, y: x + y, self.array_hz) / len(self.array_hz)
			print(value)

			return value
		else:
			return False
