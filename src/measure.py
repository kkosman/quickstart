#!/usr/bin/python3
from __future__ import print_function
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, json

import urllib.request
import urllib.parse

from sensormodules import sensor_light, sensor_dht11

import logging
logger = False
logger_handler = False

sleep_interval = 60 * 15 # 15 minutes
time_format = "%y/%m/%d %H:%M:%S"
debug = False


# PIN 18
sensor_light = sensor_light.Sensor(18) # light / color sensor
# PIN 17
sensor_dht11 = sensor_dht11.Sensor(17) # temp / humi sensor


config_path = os.path.realpath(__file__)
config_path = os.path.dirname(config_path)
user_data_path = config_path
logs_path = config_path + "/logs"

def main(argv):
    global debug, logger, logger_handler, config_path, user_data_path, logs_path
    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"d",["debug"])
    except getopt.GetoptError:
        print ('measure.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('measure.py --debug ')
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True



    if not logger:
        directory = os.path.dirname(logs_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        logger = logging.getLogger("measure")
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        logger_handler = logging.FileHandler(logs_path + "/measure.log")
        logger_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(formatter)
        logger.addHandler(logger_handler)

    logger.debug("Paths: %s, %s, %s" % (user_data_path, config_path, logs_path))

    current_date_time = datetime.now()



    ### Light sensor
    light_sensor_value = sensor_light.measure()
    ### Temp / humi sensor
    dht11_sensor_value = sensor_dht11.measure()


    try:
        url = 'https://api.thingspeak.com/update?api_key=HFQUFZZ2ZGMD9CX2' 
        url += "&field1=%s" % dht11_sensor_value[0]
        url += "&field2=%s" % dht11_sensor_value[1]
        url += "&field3=%s" % light_sensor_value
        f = urllib.request.urlopen(url)

        logger.info(f.read().decode('utf-8') + ' @ ' + url)
    except Exception as e:
        logger.error("Exception in GET request. %s" % (e) )


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        logger.info("Stopping...");

