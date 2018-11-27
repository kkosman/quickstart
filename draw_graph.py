#!/usr/bin/python3

import sys, getopt
from os import path

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

import json

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
 
from sqldata import Measure
from fourseasons import fourseasons


import matplotlib.pyplot as plt, mpld3
import numpy as np

import pandas as pd
import math


time_format = "%y/%m/%d %H:%M:%S"

#matplotlib, 
# python3-tk


def main(argv):
    cwd = path.realpath(__file__)
    cwd = path.dirname(cwd)
    with open(cwd + '/db.conf') as f:
        db_conf = f.read()
        
    engine = create_engine(db_conf)

    Session = sessionmaker(bind=engine)
    session = Session()    

    # Get all Measures
    result = session.query(Measure).order_by(Measure.date.desc())[0:2000]
    res = {'date':[],'light':[]}
    for m in result:
        res['date'].append(m.date)
        res['light'].append(m.light)


    measures = pd.DataFrame({
        # 'date': pd.to_datetime(res['date'], format=time_format),
        'date': res['date'],
        'light': res['light'],
    })
    
    measures.set_index(measures['date'])

    draw_seasons_graph()

    # draw_last_measures(res)


def draw_seasons_graph():
    fig, ax = plt.subplots()

    x = np.arange(1, 14, 0.1)
    y = fourseasons.quartic(x)

    current_x = fourseasons.get_today(datetime.now(), day_length = 20)
    print(current_x,fourseasons.quartic(current_x))

    ax.axvline(x=current_x, color='k')
    ax.plot(x, y)

    fig.savefig("test2.png")

    plt.show()
    # mpld3.show()


def draw_last_measures(measures):
    fig, ax = plt.subplots()
    # ax.plot(measures.index, measures.light)
    ax.plot(res['date'], res['light'])
    plt.xticks(rotation='vertical')

    ax.set(xlabel='date', ylabel='light',
           title='Light intensity')
    ax.grid()

    fig.savefig("test.png")

    mpld3.show()





if __name__ == '__main__':

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Stopping...");

