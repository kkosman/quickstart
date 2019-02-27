import sys
import time

try:
    import RPi.GPIO as GPIO
except:
    from .EmulatorGUI import GPIO


class Relay:
    __pin = 0
    instance = False

    def __init__(self, pin):
        self.__pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
 
        GPIO.setup(self.__pin, GPIO.OUT, initial=GPIO.HIGH)

    def set(self, on_off):
        if on_off:
            GPIO.output(self.__pin, GPIO.LOW)
        else:
            GPIO.output(self.__pin, GPIO.HIGH)

    def on(self):
        self.set(True)

    def off(self):
        self.set(False)

    def cleanup():
        GPIO.cleanup()