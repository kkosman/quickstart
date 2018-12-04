#!/usr/bin/python3

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime, timedelta

from os import path
import sys, getopt


from email.mime.text import MIMEText
from subprocess import Popen, PIPE

cwd = path.realpath(__file__)
cwd = path.dirname(cwd)


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
#1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE
# The ID and range of a sample spreadsheet.
spreadsheet_id = '10PgzjEwEv8nA-6zc7d099h4i1qp035XBhp1DFkfFmjY'
status_range_name = 'Status!B1:B'

value_input_option = 'USER_ENTERED'
time_format = "%y/%m/%d %H:%M:%S"
debug = False




def main(argv):
    global debug, spreadsheet_id

    # first check command line params
    try:
        opts, args = getopt.getopt(argv,"d",["debug"])
    except getopt.GetoptError:
        print ('check.py --debug')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('check.py --debug')
            sys.exit()
        elif opt in ("-d", "--debug"):
            # set test values
            debug = True
            spreadsheet_id = '1h8LiPEk6veikU26rA7VLptVBEJdhJyhRdL5Ft7kK1KE'

    # authorize to google api
    store = file.Storage(cwd+'/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(cwd+'/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    current_date_time = datetime.now()

    ### Check status

    # Read periods and override status
    result = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                ranges=status_range_name).execute()
    values = result.get('valueRanges', [])

    if not values:
        print('No data found.')
        sys.exit()

    
    values_tmp = values[0].get('values')
    if values_tmp:
        last_seen = datetime.strptime(values_tmp[0][0], time_format)

        if last_seen < current_date_time - timedelta(minutes=5):
            print(last_seen, "Dead")
            ### Send an notification email


            msg = MIMEText('Last seen ' + last_seen.strftime(time_format))
            msg["From"] = "notification@mikrowinnica.pl"
            msg["To"] = "krzysztof.kosman@gmail.com"
            msg["Subject"] = "Raspberry is down."
            p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
            p.communicate(msg.as_string().encode('utf-8'))

        else:
            print("Alive")


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Stopping...");


