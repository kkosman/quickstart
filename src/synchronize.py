#!/usr/bin/python3
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, requests, json, subprocess

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sensormodules import measure

import logging
logger = False
logger_handler = False

sleep_interval = 60 * 5 # 5 minutes

user_data_path = "."
config_path = "."
logs_path = "./logs"

internet_failures_count = 0

def read_and_remove(file, number = 10):
    count = 0
    lines = ""

    with open(file,'r+b', buffering=0) as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        line = ""
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            line += char.decode("utf-8") 
            # logging.info("run ", count, number, f.tell())
            if char == b'\n':
                count += 1
            if count == number + 1:
                f.truncate()
                break
            f.seek(-1, os.SEEK_CUR)
            if f.tell() == 0:
                f.truncate()
                break

        lines += line[::-1]

    return lines.split("\n")

def check_internet():
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        logger.error("No internet connection")
        return False

def main(argv):
    global sleep_interval, config_path, user_data_path, logs_path, logger, logger_handler, internet_failures_count
    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"ht",["test","debug"])
    except getopt.GetoptError:
        print('synchronize.py -h')
        sys.exit(2)
    debug = False
    for opt, arg in opts:
        if opt == '-h':
            print('synchronize.py --debug')
            sys.exit()
        elif opt in ("-t", "--test"):
            # set test values
            sleep_interval = 5 # seconds
        elif opt in ("--debug"):
            debug = True

    if 'SNAP_COMMON' in os.environ:
        user_data_path = os.environ['SNAP_COMMON']
        config_path = os.environ['SNAP_DATA']
        logs_path = os.environ['SNAP_COMMON']

    if not logger:
        directory = os.path.dirname(logs_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        logger = logging.getLogger("quicksynch")
        logger.setLevel(logging.DEBUG if debug else logging.ERROR)
        logger_handler = logging.FileHandler(logs_path + "/quicksynch.log")
        logger_handler.setLevel(logging.DEBUG if debug else logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(formatter)
        logger.addHandler(logger_handler)

    if not check_internet():
        ## just a concept for restarting networking

        # internet_failures_count += 1
        # if internet_failures_count == 2:
        #     logger.error("Internet is not available second time, attempting to restart wlan0", lines)
        #     subprocess.Popen("/sbin/ifdown 'wlan0'".split(), stdout=subprocess.PIPE)
        #     # output, error = process.communicate()            
        #     sleep(5)
        #     subprocess.Popen("/sbin/ifup --force 'wlan0'".split(), stdout=subprocess.PIPE)

        #     internet_failures_count = 0

        return

    while True:

        try:
            lines = read_and_remove(user_data_path + "/.data_store", number=10)
        except FileNotFoundError as e:
            logger.error("Nofile %s" % (user_data_path + "/.data_store"))
            return

        if not lines:
            logger.error("Wrong lines object", lines)
            break

        if len(str(lines)) < 10:
            logger.debug("No more lines to process.")
            break


        logger.debug("entring lines: %s" % lines)
        for line in lines:
            logger.debug("proces line: %s" % line)
            try:
                v = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            
            measure_object = measure.Measure( user_data_path = user_data_path, config_path = config_path )
            measure_object.date = v[0]
            measure_object.temperature = v[1]
            measure_object.humidity = v[2]
            measure_object.light = v[3]
            measure_object.save()
            logger.debug("processed line")

        sleep(5) # wait not to overkill DB connection, we are not in a hustle


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            logger.debug("Going to sleep for %s" % sleep_interval)
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        logger.info("Stopping...");

