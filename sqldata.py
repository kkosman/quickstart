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
 
Base = declarative_base()
cwd = path.realpath(__file__)
cwd = path.dirname(cwd)
with open(cwd + '/db.conf') as f:
    db_conf = f.read()
    
engine = create_engine(db_conf)
time_format = "%y/%m/%d %H:%M:%S"

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
#1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE
# The ID and range of a sample spreadsheet.
light_range_name = 'Light!A:B'
pump_range_name = 'PumpPeriods!A:B'
pump_done_range_name = 'PumpPeriods!B'
status_range_name = 'Status!B1:B'
periods_range_name = ['Light!A2:A','LightPeriods!A2:C']
sensor_stats_range_name = 'SensorStats!A2:D'

value_input_option = 'USER_ENTERED'
 
class Measure(Base):
    __tablename__ = 'measure'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    temperature = Column(Float(precision=2), nullable=False)
    humidity = Column(Float(precision=2), nullable=False)
    light = Column(Float(precision=2), nullable=False)

    def save(self, spreadsheet=False):
        if spreadsheet:
            # store to google drive
            body = {'values': self.get_values()}

            # authorize to google api
            store = file.Storage(cwd+'/token.json')
            creds = store.get()
            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(cwd+'/credentials.json', SCOPES)
                creds = tools.run_flow(flow, store)
            service = build('sheets', 'v4', http=creds.authorize(Http()))

            result = service.spreadsheets().values().update(spreadsheetId=spreadsheet, range=status_range_name,
                valueInputOption=value_input_option, body=body).execute()

        #store to SQL DB
        Session = sessionmaker(bind=engine)
        session = Session()    
        session.add(self)
        session.commit()

    def store(self):
        open(cwd + '/.data_store','a').write(json.dumps(self.get_values()) + '\n')

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


            open(cwd + '/.data_store','w').write('')
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
