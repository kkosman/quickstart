#!/usr/bin/python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime

from time import sleep
from os import path

cwd = path.realpath(__file__)
cwd = path.dirname(cwd)

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
spreadsheet_id = '10PgzjEwEv8nA-6zc7d099h4i1qp035XBhp1DFkfFmjY'
range_name = 'Light!A:B'
periods_range_name = 'Periods!A2:C'
value_input_option = 'USER_ENTERED'
status = 'off'
time_format = "%y/%m/%d %H:%M:%S"

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    global status;


    store = file.Storage(cwd+'/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(cwd+'/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    status = 'on' if status == 'off' else 'off'


    # Read periods and override status
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                range=periods_range_name).execute()
    values = result.get('values', [])
    update_status = False

    if not values:
        print('No data found.')
    else:
        for row in values:
            a = datetime.strptime(row[0], time_format)
            b = datetime.strptime(row[1], time_format)
            if a <= datetime.now() and b >= datetime.now():
                if status != row[2]:
                    status = row[2]
                    update_status = True
                    break


    if update_status:
        # Call the Sheets API
        values = [[ status, datetime.now().strftime(time_format) ]]
        body = {'values': values}

        result = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()

        print('{0} rows updated.'.format(result.get('updates').get('updatedRows')));


if __name__ == '__main__':

    try:
        while True:
            main()
            sleep(900) #15 minutes
    except KeyboardInterrupt:
        print("Stopping...");

