#!/usr/bin/python3
from __future__ import print_function
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, json, subprocess

import urllib.request
import urllib.parse

from sensormodules.relay import Relay
from sensormodules.fourseasons import fourseasons



import logging
logger = False
logger_handler = False


sleep_interval = 10 # seconds
sync_interval = 60 * 30 # 15 minutes
sensor_read_interval = 60 * 5 # 5 minutes
pump_interval = 5 # minutes
night_pump_interval = 60 # minutes
water_duration = 30 # seconds
light_status = 'off'
pump_status = 'off'
time_format = "%y/%m/%d %H:%M:%S"
debug = False


relay_in1 = Relay(12) # light
relay_in2 = Relay(16) # water


config_path = os.path.realpath(__file__)
config_path = os.path.dirname(config_path)
user_data_path = config_path
logs_path = config_path + "/logs"



def main(argv):
    global light_status, pump_status, debug, sleep_interval, sensor_read_interval, sync_interval, pump_interval, night_pump_interval, water_duration , logger, logger_handler, config_path, user_data_path, logs_path
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
            'last_water': (current_date_time - timedelta(minutes=100)).strftime(time_format),
            'last_sync': (current_date_time - timedelta(minutes=100)).strftime(time_format),
            'last_sensor_read': (current_date_time - timedelta(minutes=100)).strftime(time_format),
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
    logger.debug("It is a " + light_status)

    # Send status to the relay
    if prev_light_status != light_status:
        logger.debug("Light change send")
        relay_in1.set(light_status == "day")


    ### Process light sensor subprocess

    last_sync = datetime.strptime(status_dict['last_sync'], time_format)
    if last_sync < current_date_time - timedelta(seconds=sync_interval):
        status_dict['last_sync'] = current_date_time.strftime(time_format)
        logger.debug("Light sensor sychronization")

        with open(config_path + '/light_sensor_status','r') as file:
            read = file.read()
            logger.debug("Previous sensor read: %s" % read)
            if read != "" and "error" not in read:
                logger.debug("Send output")

                try:
                    url = 'https://api.thingspeak.com/update?api_key=HFQUFZZ2ZGMD9CX2' 
                    # url += "&field1=%s" % dht11_sensor_value[0]
                    # url += "&field2=%s" % dht11_sensor_value[1]
                    url += "&field3=%s" % read.split()[-2]
                    f = urllib.request.urlopen(url)

                    logger.info(f.read().decode('utf-8') + ' @ ' + url)
                except Exception as e:
                    logger.error("Exception in GET request. %s" % (e) )

    last_sensor_read = datetime.strptime(status_dict['last_sensor_read'], time_format)
    if last_sensor_read < current_date_time - timedelta(seconds=sensor_read_interval):
        status_dict['last_sensor_read'] = current_date_time.strftime(time_format)
        logger.debug("Light sensor read start")
        command = config_path + '/sensormodules/tsl235r/tsl_read 300000 10'
        # command = "sleep 60 && echo 'TSL235READ--poll_time--itterations--avg_value--autoscale 300000 10 0.028 17'"
        with open(config_path + '/light_sensor_status',"wb") as out:
            subprocess.Popen(command, shell=True, stdout=out, stderr=out)



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

