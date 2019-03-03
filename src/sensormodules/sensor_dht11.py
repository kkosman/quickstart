#!/usr/bin/python3
# PIN 17

import sys
import time
from functools import reduce

try:
    import RPi.GPIO as GPIO
except:
    from .EmulatorGUI import GPIO

from . import dht11


class Sensor:
    __pin = 0
    instance = False
    array_temp = []
    array_humi = []

    def __init__(self, pin):
        self.__pin = pin
        GPIO.setmode(GPIO.BCM)

        self.instance = dht11.DHT11(pin = self.__pin)

    def measure(self):
        x = 0
        self.array_temp = []
        self.array_humi = []
        while x < 5:
            x += 1
            result = self.instance.read()

            if result.is_valid():
                print("Temperature: %d C" % result.temperature)
                self.array_temp.append(result.temperature)
                print("Humidity: %d %%" % result.humidity)
                self.array_humi.append(result.humidity)
            else:
                print("Error: %d" % result.error_code)

            time.sleep(6)

        value_temp = reduce(lambda x, y: x + y, self.array_temp) / len(self.array_temp) if len(self.array_temp) > 1 else False
        value_humi = reduce(lambda x, y: x + y, self.array_humi) / len(self.array_humi) if len(self.array_humi) > 1 else False
        print(value_temp, value_humi)

        return [value_temp, value_humi];


if __name__ == '__main__':

    try:
        config_path = os.path.realpath(__file__)
        config_path = os.path.dirname(config_path)
        # PIN 17
        sensor_dht11 = sensor_dht11.Sensor(17) # temp / humi sensor
        ### Temp / humi sensor
        dht11_sensor_value = sensor_dht11.measure()
        with open(config_path + '/dht_sensor_status',"wb") as out:
            out.write(dht11_sensor_value)
            out.truncate()
            
    except KeyboardInterrupt:
        logger.debug("Stopping...")


