#!/usr/bin/python3

import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from time import sleep
 
Base = declarative_base()
 
class Measure(Base):
    __tablename__ = 'measure'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    temperature = Column(Float(precision=2), nullable=False)
    humidity = Column(Float(precision=2), nullable=False)
    light = Column(Float(precision=2), nullable=False)
 
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
with open('db.conf') as f:
    db_conf = f.read()
    
engine = create_engine(db_conf)

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

# Session = sessionmaker(bind=engine)
# session = Session()


# x = 0
# max = 100
# while x < max:
# 	x += 1
# 	measure = Measure(date=datetime.now(), temperature=1.1 + x, humidity=0.85, light=12333.1)
# 	session.add(measure)

# 	print('{}/{} \n'.format(x,max))

# session.commit()
