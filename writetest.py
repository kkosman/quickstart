#!/usr/bin/python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime

from time import sleep
from os import path
import sys, getopt

cwd = path.realpath(__file__)
cwd = path.dirname(cwd)

sleep_interval = 900
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
#1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE
# The ID and range of a sample spreadsheet.
spreadsheet_id = '10PgzjEwEv8nA-6zc7d099h4i1qp035XBhp1DFkfFmjY'
range_name = 'Light!A:B'
status_range_name = 'Status!B1:B'
periods_range_name = ['Light!A2:A','Periods!A2:C']
value_input_option = 'USER_ENTERED'
status = 'off'
time_format = "%y/%m/%d %H:%M:%S"

def main(argv):
    global status, spreadsheet_id, sleep_interval;

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
            sleep_interval = 10
            spreadsheet_id = '1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE'

    # authorize to google api
    store = file.Storage(cwd+'/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(cwd+'/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Read periods and override status
    result = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                ranges=periods_range_name).execute()

    values = result.get('valueRanges', [])
    current_date_time = datetime.now()

    if not values:
        print('No data found.')
        sys.exit()

    values_tmp = values[0].get('values')
    if values_tmp:
        status = values_tmp[-1][-1]

    update_status = False
    for row in values[1].get('values'):
        a = datetime.strptime(row[0], time_format)
        b = datetime.strptime(row[1], time_format)
        if a <= current_date_time and b >= current_date_time:
            if status != row[2]:
                status = row[2]
                update_status = True
                break


    if update_status:
        # Call the Sheets API
        values = [[ status, current_date_time.strftime(time_format) ]]
        body = {'values': values}

        result = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()

        print('{0} rows updated.'.format(result.get('updates').get('updatedRows')));
    else:
        print('No update required')

    #update system status
    values = [
        [ current_date_time.strftime(time_format) ],
        [ "?C" ],
        [ "?%" ],
        [ "n/d" ],
        [ status ],
        [ 'n/d' ]
    ]
    body = {'values': values}

    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=status_range_name,
        valueInputOption=value_input_option, body=body).execute()


if __name__ == '__main__':

    try:
        while True:
            main(sys.argv[1:])
            sleep(sleep_interval)
    except KeyboardInterrupt:
        print("Stopping...");

