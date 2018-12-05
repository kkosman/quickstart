#!/usr/bin/python3
from datetime import datetime, timedelta

from time import sleep
import sys, getopt, os, requests, json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sensormodules import measure
################
# co z pustym plikiem!?

sleep_interval = 5 # seconds

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
            if char == b'\n':
                count += 1
            if count == number + 1:
                f.truncate()
                break
            f.seek(-1, os.SEEK_CUR)

        lines += line[::-1]

    return lines.split("\n")

def check_internet():
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection")
    return False

def main(argv):

    if not check_internet():
        # maybe additional sleep?
        return

    if 'SNAP_USER_DATA' in os.environ:
        user_data_path = os.environ['SNAP_USER_DATA']
        config_path = os.environ['SNAP_DATA']
    else:
        user_data_path = "./src/"
        config_path = "./src/"


    lines = read_and_remove(user_data_path + "/.data_store", number=10)
    if not lines:
        print("Wrong lines object", lines)
        return


    for line in lines:
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


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
            
    except KeyboardInterrupt:
        print("Stopping...");

