#!/usr/bin/python3

import sys, getopt
import os

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

import json

Base = declarative_base()

if 'SNAP_USER_DATA' in os.environ:
    cwd = os.environ['SNAP_USER_DATA']
    with open(os.environ['SNAP_DATA'] + '/db.conf') as f:
        db_conf = f.read()
else:
    cwd = os.path.realpath(__file__)
    cwd = os.path.dirname(cwd)
    with open(cwd + '/db.conf') as f:
        db_conf = f.read()
    
    
engine = create_engine(db_conf)
time_format = "%y/%m/%d %H:%M:%S"

 
class Measure(Base):
    __tablename__ = 'measure'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    temperature = Column(Float(precision=2), nullable=False)
    humidity = Column(Float(precision=2), nullable=False)
    light = Column(Float(precision=2), nullable=False)

    def save(self):
        #store to SQL DB
        Session = sessionmaker(bind=engine)
        session = Session()    
        session.add(self)
        session.commit()

    def store(self):
        # Get status from a file
        try:
            fs = open(cwd + '/.data_store','a')
        except:
            fs = open(cwd + '/.data_store','w')

        fs.write(json.dumps(self.get_values()) + '\n')
        fs.close()

    def restore(self):
        try:
            with open(cwd + '/.data_store','r') as file:
                for line in file:
                    v = json.loads(line)
                    measure = Measure(date=v[0], 
                                temperature=v[1], 
                                humidity=v[2], 
                                light=v[3])
                    measure.save()


            fs = open(cwd + '/.data_store','w')
            fs.write('')
            fs.close()
        except Exception as e:
            print("failed to restore! ", e)

    def get_values(self):
        return [
            [ self.date.strftime(time_format) ],
            [ self.temperature ],
            [ self.humidity ],
            [ self.light ]
        ]


def main(argv):
    global engine

    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"i",["init"])
    except getopt.GetoptError:
        print ('sqldata.py --init')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('sqldata.py --init')
            sys.exit()
        elif opt in ("-i", "--init"):
            Base.metadata.create_all(engine)



if __name__ == '__main__':

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Stopping...");

