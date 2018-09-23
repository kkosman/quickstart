#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep
from DHT11 import dht11


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

DHTinstance = dht11.DHT11(pin = 17)

while True:

    result = DHTinstance.read()

    if result.is_valid():
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
    else:
        print("Error: %d" % result.error_code)

    sleep(3)
