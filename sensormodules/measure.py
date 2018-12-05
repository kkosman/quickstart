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

time_format = "%y/%m/%d %H:%M:%S"

 
class Measure(Base):
    __tablename__ = 'measure'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    temperature = Column(Float(precision=2), nullable=False)
    humidity = Column(Float(precision=2), nullable=False)
    light = Column(Float(precision=2), nullable=False)
    user_data_path = False
    config_path = False
    engine = False

    def __init__(self, user_data_path = False, config_path = False):

        if user_data_path:
            self.user_data_path = user_data_path
        if config_path:
            self.config_path = config_path

        if not user_data_path and 'SNAP_USER_DATA' in os.environ:
            self.user_data_path = os.environ['SNAP_USER_DATA']
            self.config_path = os.environ['SNAP_DATA']


        with open(self.config_path + '/db.conf') as f:
            db_conf = f.read()
            
        self.engine = create_engine(db_conf)

    def save(self):
        #store to SQL DB
        Session = sessionmaker(bind=self.engine)
        session = Session()    
        session.add(self)
        session.commit()

    def store(self):
        # Get status from a file
        try:
            fs = open(self.user_data_path + '/.data_store','a')
        except:
            fs = open(self.user_data_path + '/.data_store','w')

        fs.write(json.dumps(self.get_values()) + "\n")
        fs.close()

    def get_values(self):
        return [
            [ self.date.strftime(time_format) ],
            [ self.temperature ],
            [ self.humidity ],
            [ self.light ]
        ]

