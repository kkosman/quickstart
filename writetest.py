#!/usr/bin/python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime, timedelta

from time import sleep
from os import path
import sys, getopt

from modules import relay, sensor_light, sensor_dht11
from sqldata import Measure
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

cwd = path.realpath(__file__)
cwd = path.dirname(cwd)

sleep_interval = 60 # seconds
pump_interval = 60 # seconds
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
#1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE
# The ID and range of a sample spreadsheet.
spreadsheet_id = '10PgzjEwEv8nA-6zc7d099h4i1qp035XBhp1DFkfFmjY'
light_range_name = 'Light!A:B'
pump_range_name = 'PumpPeriods!A:B'
pump_done_range_name = 'PumpPeriods!B'
status_range_name = 'Status!B1:B'
periods_range_name = ['Light!A2:A','LightPeriods!A2:C']
sensor_stats_range_name = 'SensorStats!A2:D'

value_input_option = 'USER_ENTERED'
light_status = 'off'
pump_status = 'off'
time_format = "%y/%m/%d %H:%M:%S"
debug = False

# IN 1,2,3,4 -> PIN 12,16,20,21
relay_in1 = relay.Relay(12) # light
relay_in2 = relay.Relay(16) # water
# relay_in3 = Relay(20) # free slot
# relay_in4 = Relay(21) # free slot

# PIN 18
sensor_light = sensor_light.Sensor(18) # light / color sensor
# PIN 17
sensor_dht11 = sensor_dht11.Sensor(17) # temp / humi sensor

def main(argv):
    global light_status, pump_status, spreadsheet_id, debug, sleep_interval, pump_interval;

    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"d",["debug"])
    except getopt.GetoptError:
        print ('writetest.py --debug')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('writetest.py --debug')
            sys.exit()
        elif opt in ("-d", "--debug"):
            # set test values
            sleep_interval = 10 # seconds
            pump_interval = 30 # seconds
            debug = True
            spreadsheet_id = '1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE'

    # authorize to google api
    store = file.Storage(cwd+'/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(cwd+'/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))


    # connect to sql DB
    engine = create_engine('mysql://kosmani2_wine:FwzsfV1q@kosman.com.pl/kosmani2_wine')
    Session = sessionmaker(bind=engine)
    session = Session()    

    current_date_time = datetime.now()

    ### Light status

    # Read periods and override status
    result = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                ranges=periods_range_name).execute()
    values = result.get('valueRanges', [])

    if not values:
        print('No data found.')
        sys.exit()

    values_tmp = values[0].get('values')
    if values_tmp:
        light_status = values_tmp[-1][-1]

    update_status = False
    for row in values[1].get('values'):
        a = datetime.strptime(row[0], time_format)
        b = datetime.strptime(row[1], time_format)
        if a <= current_date_time and b >= current_date_time:
            if light_status != row[2]:
                light_status = row[2]
                update_status = True
                break


    if update_status:
        # Send status to the relay
        relay_in1.set(light_status == "on")


        # Call the Sheets API
        values = [[ light_status, current_date_time.strftime(time_format) ]]
        body = {'values': values}

        result = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=light_range_name,
            valueInputOption=value_input_option, body=body).execute()

        print('Light: {0} rows updated.'.format(result.get('updates').get('updatedRows')));
    else:
        print('Light: No update required')

    ### Pump status
    if pump_status == "off":
        # 
        # Read pump periods and turn it on if needed
        # 
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                    range=pump_range_name).execute()

        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            sys.exit()

        update_status = False
        x = 1
        for row in values[1:]:
            x += 1
            a = datetime.strptime(row[0], time_format)
            if len(row) == 1 and a <= current_date_time:
                update_status = True
                break

        if update_status:
            # Send status to the relay
            relay_in2.set(True)
            pump_status = current_date_time
            body = {'values': [ [ "done" ] ]}
            result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=pump_done_range_name + str(x),
                valueInputOption=value_input_option, body=body).execute()
        else:
            print('Pump: No update required')

    else:
        if pump_status < current_date_time - timedelta(seconds=pump_interval):
            # Send status to the relay
            relay_in2.set(False)
            pump_status = "off"
            print('Pump: Shut down')
        else:
            print('Pump: nothing to do, still watering')

    ### Light sensor
    light_sensor_value = sensor_light.measure()

    ### Temp / humi sensor
    dht11_sensor_value = sensor_dht11.measure()

    # update system status
    values = [
        [ current_date_time.strftime(time_format) ],
        [ dht11_sensor_value[0] ],
        [ dht11_sensor_value[1] ],
        [ light_sensor_value ],
        [ light_status ],
        [ pump_status.strftime(time_format) if type(pump_status) is datetime else pump_status]
    ]
    body = {'values': values}

    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=status_range_name,
        valueInputOption=value_input_option, body=body).execute()

    # update sensor stats

    measure = Measure(date=current_date_time, temperature=dht11_sensor_value[0], humidity=dht11_sensor_value[1], light=light_sensor_value)
    session.add(measure)
    session.commit()


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
    except KeyboardInterrupt:
        print("Stopping...");

