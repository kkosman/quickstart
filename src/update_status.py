#!/usr/bin/python3

import sys, getopt
from os import path

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from tabulate import tabulate

import json
 
from sqldata import Measure
import fourseasons



time_format = "%y/%m/%d %H:%M:%S"


def main(argv):
    cwd = path.realpath(__file__)
    cwd = path.dirname(cwd)
    with open(cwd + '/db.conf') as f:
        db_conf = f.read()
        
    engine = create_engine(db_conf)

    Session = sessionmaker(bind=engine)
    session = Session()    

    result = session.query(Measure).order_by(Measure.date.desc()).first()
    valid = "Valid" if result.date > (datetime.now() - timedelta(minutes=30)) else "Invalid"

    output = '''Last seen: %s %s
Temperature: %d
Humidity: %d
Light: %d'''	% (result.date, valid, result.temperature, result.humidity, result.light)

    # draw seasons

    results = []

    x = 0
    while x < 10:
        current_date_time = datetime.now() + timedelta(hours=30*24*x)
        # current_date_time = datetime.now() + timedelta(hours=4*x)
        season = fourseasons.fourseasons(current_date_time)
        today = season.get_today()
        day_length = season.get_daylength()
        light_status = season.is_it_night_or_day()
        results.append([current_date_time,light_status,today, day_length])
        x+=1

    next_10_months = tabulate(results,headers=['date', 'light', 'today', 'day_length'])

    results = []

    x = 0
    while x < 12:
        current_date_time = datetime.now() + timedelta(hours=2*x)
        season = fourseasons.fourseasons(current_date_time)
        today = season.get_today()
        day_length = season.get_daylength()
        light_status = season.is_it_night_or_day()
        results.append([current_date_time,light_status,today, day_length])
        x+=1

    next_24_hours = tabulate(results,headers=['date', 'light', 'today', 'day_length'])

    output += '''

###### Next 10 months
%s

###### Next 24 hours
%s
''' % (next_10_months, next_24_hours)
    


    status_file = open(cwd + '/status.txt','w')
    status_file.write(output)
    status_file.truncate()
    status_file.close()



if __name__ == '__main__':

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Stopping...");

