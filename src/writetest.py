#!/usr/bin/python3
from __future__ import print_function
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os

from modules import relay, sensor_light, sensor_dht11
from sqldata import Measure
from fourseasons import fourseasons
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import json



if 'SNAP_USER_DATA' in os.environ:
    cwd = os.environ['SNAP_USER_DATA']
else:
    cwd = os.path.realpath(__file__)
    cwd = os.path.dirname(cwd)

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

def main(argv):
    global light_status, pump_status, debug, sleep_interval, pump_interval, water_duration 
    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"dt",["debug","test"])
    except getopt.GetoptError:
        print ('writetest.py --debug')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('writetest.py --debug')
            sys.exit()
        elif opt in ("-d", "--debug"):
            # set test values
            sleep_interval = 1 # seconds
            pump_interval = 0.1 # minutes
            water_duration = 10 # seconds
            debug = True
        elif opt in ("-t", "--test"):
            # set test values
            sleep_interval = 1 # seconds
            pump_interval = 0.1 # minutes
            water_duration = 10 # seconds

    current_date_time = datetime.now()

    # Get status from a file
    try:
        status_file = open(cwd + '/status.json','r')
        status_dict = json.loads(status_file.read())
        status_file.close()
    except Exception as e:
        status_dict = {
            'is_watering': False,
            'last_water': (current_date_time - timedelta(minutes=100)).strftime(time_format)
        }

        status_file = open(cwd + '/status.json','w')
        status_file.write(json.dumps(status_dict))
        status_file.truncate()
        status_file.close()

        print("Trying to create a new status file. Exception: ", e)
    
    pump_status = datetime.strptime(status_dict['last_water'], time_format)


    # Process if we should water
    if status_dict['is_watering'] and pump_status < current_date_time - timedelta(seconds=water_duration): # we should stop watering
        status_dict['is_watering'] = False
        relay_in2.set(False)
        print("Watering: stop",pump_status, current_date_time - timedelta(seconds=water_duration))

    elif not status_dict['is_watering'] and pump_status < current_date_time - timedelta(minutes=pump_interval): # we should start watering
        status_dict['last_water'] = current_date_time.strftime(time_format)
        status_dict['is_watering'] = True
        relay_in2.set(True)
        print("Watering: start",pump_status, current_date_time - timedelta(minutes=pump_interval))

    else: # nothing to do
        print("Watering: nothing to change")


    ### Light status update
    season = fourseasons(current_date_time)
    light_status = season.is_it_night_or_day()
    # Send status to the relay
    relay_in1.set(light_status == "day")


    status_file = open(cwd + '/status.json','w')
    status_file.write(json.dumps(status_dict))
    status_file.truncate()
    status_file.close()


    ### Light sensor
    light_sensor_value = sensor_light.measure()
    ### Temp / humi sensor
    dht11_sensor_value = sensor_dht11.measure()


    # update system status
    measure = Measure(date=current_date_time, 
                    temperature=dht11_sensor_value[0], 
                    humidity=dht11_sensor_value[1], 
                    light=light_sensor_value)


    try:
        measure.save()
        measure.restore()
    except Exception as e:
        measure.store()
        print("Some problem storing status, saving for later. Exception: ", e)


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        print("Stopping...");

