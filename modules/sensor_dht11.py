#!/usr/bin/python3
# PIN 17

import sys
import time

mockup = False
try:
	import RPi.GPIO as GPIO
	from libs.DHT11 import dht11
except ImportError:
    mockup = True
    print("No RPi, working with mockup Sensor DHT11")


class Sensor:
	global mockup
	__pin = 0
	instance = False
	array_temp = []
	array_humi = []

	def __init__(self, pin):
		self.__pin = pin
		if mockup:
			self.instance = MockupSensor(self.__pin)
		else:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.__pin, GPIO.IN)

			self.instance = dht11.DHT11(pin = self.__pin)

	def measure(self):
		if mockup:
			return [24,65]

		x = 0
		self.array_temp = []
		self.array_humi = []
		while x < 10:
			x += 1
			result = self.instance.read()

			if result.is_valid():
				print("Temperature: %d C" % result.temperature)
				self.array_temp.push(result.temperature)
				print("Humidity: %d %%" % result.humidity)
				self.array_humi.push(result.humidity)
			else:
				print("Error: %d" % result.error_code)

			sleep(10)

		value_temp = reduce(lambda x, y: x + y, self.array_temp) / len(self.array_temp)
		value_humi = reduce(lambda x, y: x + y, self.array_humi) / len(self.array_humi)
		print(value_temp, value_humi)

		return [value_temp, value_humi];


class MockupSensor:
    __pin = 0
    def __init__(self, pin):
        self.__pin = pin

    def read():
    	return MockupSensorResult()



class MockupSensorResult:
	temperature = 25
	humidity = 60

	def __init__(self):
		return

	def is_valid(self):
		return True
