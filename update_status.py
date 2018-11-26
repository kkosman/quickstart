#!/usr/bin/python3

import sys, getopt
from os import path

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta

import json
 
from sqldata import Measure



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
    valid = "Valid" if datetime.now() > result.date - timedelta(minutes=5) else "Invalid"

    output = '''Last seen: %s %s
Temperature: %d
Humidity: %d
Light: %d'''	% (result.date, valid, result.temperature, result.humidity, result.light)


    status_file = open(cwd + '/status.txt','w')
    status_file.write(output)
    status_file.truncate()
    status_file.close()



if __name__ == '__main__':

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Stopping...");

