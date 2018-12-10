#!/usr/bin/python3
from __future__ import print_function
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, json

from sensormodules import relay, sensor_light, sensor_dht11, measure, fourseasons


import logging
logger = False
logger_handler = False


sleep_interval = 60 # seconds
pump_interval = 60 # minutes
water_duration = 60 # seconds
light_status = 'off'
pump_status = 'off'
time_format = "%y/%m/%d %H:%M:%S"
debug = False


# IN 1,2,3,4 -> PIN 12,16,20,21
relay_in1 = relay.Relay(12) # light
relay_in2 = relay.Relay(16) # water
# relay_in3 = Relay(20) # free slot
# relay_in4 = Relay(21) # free slot

# PIN 18
sensor_light = sensor_light.Sensor(18) # light / color sensor
# PIN 17
sensor_dht11 = sensor_dht11.Sensor(17) # temp / humi sensor


config_path = os.path.realpath(__file__)
config_path = os.path.dirname(config_path)
user_data_path = config_path
logs_path = config_path + "/logs"

def main(argv):
    global light_status, pump_status, debug, sleep_interval, pump_interval, water_duration , logger, logger_handler, config_path, user_data_path, logs_path
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


    if 'SNAP_COMMON' in os.environ:
        config_path = os.environ['SNAP_DATA']
        user_data_path = os.environ['SNAP_COMMON']
        logs_path = os.environ['SNAP_COMMON']

    if not logger:
        directory = os.path.dirname(logs_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        logger = logging.getLogger("quickstart")
        logger.setLevel(logging.DEBUG if debug else logging.ERROR)
        logger_handler = logging.FileHandler(logs_path + "/quickstart.log")
        logger_handler.setLevel(logging.DEBUG if debug else logging.ERROR)
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
    
    pump_status = datetime.strptime(status_dict['last_water'], time_format)


    # Process if we should water
    if status_dict['is_watering'] and pump_status < current_date_time - timedelta(seconds=water_duration): # we should stop watering
        status_dict['is_watering'] = False
        relay_in2.set(False)
        logger.debug("Watering: stop",pump_status, current_date_time - timedelta(seconds=water_duration))

    elif not status_dict['is_watering'] and pump_status < current_date_time - timedelta(minutes=pump_interval): # we should start watering
        status_dict['last_water'] = current_date_time.strftime(time_format)
        status_dict['is_watering'] = True
        relay_in2.set(True)
        logger.debug("Watering: start",pump_status, current_date_time - timedelta(minutes=pump_interval))

    else: # nothing to do
        logger.debug("Watering: nothing to change")


    ### Light status update
    season = fourseasons.fourseasons(current_date_time)
    light_status = season.is_it_night_or_day()
    # Send status to the relay
    relay_in1.set(light_status == "day")


    status_file = open(user_data_path + '/status.json','w')
    status_content = json.dumps(status_dict)
    status_file.write(status_content)
    status_file.truncate()
    status_file.close()


    ### Light sensor
    light_sensor_value = sensor_light.measure()
    ### Temp / humi sensor
    dht11_sensor_value = sensor_dht11.measure()


    # update system status
    measure_object = measure.Measure( user_data_path = user_data_path, config_path = config_path )
    measure_object.date = current_date_time
    measure_object.temperature = dht11_sensor_value[0]
    measure_object.humidity = dht11_sensor_value[1]
    measure_object.light = light_sensor_value
    measure_object.store()


    logger.debug("Sensors: %s, %s ; Light status: %s ; Status: %s" % (light_sensor_value, dht11_sensor_value ,light_status, status_content))


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        logger.info("Stopping...");

