#!/usr/bin/python3
from __future__ import print_function
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, json

from sensormodules.relay import Relay
from sensormodules.fourseasons import fourseasons



import logging
logger = False
logger_handler = False


sleep_interval = 10 # seconds
pump_interval = 5 # minutes
night_pump_interval = 60 # minutes
water_duration = 30 # seconds
light_status = 'off'
pump_status = 'off'
time_format = "%y/%m/%d %H:%M:%S"
debug = False


# IN 1,2,3,4 -> PIN 12,16,20,21
relay_in1 = Relay(12) # light
relay_in2 = Relay(16) # water
# relay_in3 = Relay(20) # free slot
# relay_in4 = Relay(21) # free slot


config_path = os.path.realpath(__file__)
config_path = os.path.dirname(config_path)
user_data_path = config_path
logs_path = config_path + "/logs"

def main(argv):
    global light_status, pump_status, debug, sleep_interval, pump_interval, night_pump_interval, water_duration , logger, logger_handler, config_path, user_data_path, logs_path
    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"dt",["debug","test"])
    except getopt.GetoptError:
        print ('writetest.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('writetest.py --debug --test ')
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-t", "--test"):
            # set test values
            sleep_interval = 1 # seconds
            pump_interval = 0.1 # minutes
            water_duration = 10 # seconds


    if not logger:
        directory = os.path.dirname(logs_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        logger = logging.getLogger("quickstart")
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        logger_handler = logging.FileHandler(logs_path + "/quickstart.log")
        logger_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(formatter)
        logger.addHandler(logger_handler)

    logger.debug("Paths: %s, %s, %s" % (user_data_path, config_path, logs_path))

    current_date_time = datetime.now()

    # Get status from a file
    try:
        status_file = open(user_data_path + '/status.json','r')
        status_dict = json.loads(status_file.read())
        status_file.close()
    except Exception as e:
        status_dict = {
            'is_watering': False,
            'last_water': (current_date_time - timedelta(minutes=100)).strftime(time_format)
        }

        status_file = open(user_data_path + '/status.json','w')
        status_file.write(json.dumps(status_dict))
        status_file.truncate()
        status_file.close()

        logger.warning("Trying to create a new status file. Exception: ", e)
    

    ### Light status update
    season = fourseasons(current_date_time)

    prev_light_status =  light_status
    light_status = season.is_it_night_or_day()
    # Send status to the relay
    if prev_light_status != light_status:
        logger.debug("Light change send")
        relay_in1.set(light_status == "day")


    ### Process if we should water
    pump_status = datetime.strptime(status_dict['last_water'], time_format)
    if light_status == "day":
        interval = pump_interval
    else:
        interval = night_pump_interval


    if status_dict['is_watering'] and pump_status < current_date_time - timedelta(seconds=water_duration): # we should stop watering
        status_dict['is_watering'] = False
        relay_in2.set(False)
        logger.debug("Watering: stop %s %s" % (pump_status, current_date_time - timedelta(seconds=water_duration)))

    elif not status_dict['is_watering'] and pump_status < current_date_time - timedelta(minutes=interval): # we should start watering
        status_dict['last_water'] = current_date_time.strftime(time_format)
        status_dict['is_watering'] = True
        relay_in2.set(True)
        logger.debug("Watering: start %s %s" % (pump_status, current_date_time - timedelta(minutes=interval)))

    else: # nothing to do
        logger.debug("Watering: nothing to change")



    status_file = open(user_data_path + '/status.json','w')
    status_content = json.dumps(status_dict)
    status_file.write(status_content)
    status_file.truncate()
    status_file.close()

    logger.info(status_content)


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        logger.debug("Stopping...")

    finally:
        logger.debug("Cleanup...")
        Relay.cleanup()

