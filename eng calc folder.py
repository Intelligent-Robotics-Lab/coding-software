import os
import pandas as pd
from datetime import date
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
import pprint
from itertools import chain

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.readonly","https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1XRe0mP6fpAo8PbTtV4pGgT0RTKWcVoTGWKhxxJkhtis'
ranges = ['Sheet3!A:A','Sheet3!B:B','Sheet3!C:C','Sheet3!D:D','Sheet3!E:E']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service_sheets = build('sheets', 'v4', credentials=creds)
         # Call the Sheets API
        sheet = service_sheets.spreadsheets()
        result = sheet.values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    ranges=ranges).execute()
        values = result.get('valueRanges', [])
        columns_list = []
        for i in range(3):
            column = list(chain.from_iterable(values[i]['values']))
            columns_list.append(column)
        zipped_values = list(zip(*columns_list))
        #pprint.pprint(zipped_values)
        start_intervals = list(chain.from_iterable(values[3]['values']))
        end_intervals = list(chain.from_iterable(values[4]['values']))
        interval_ranges = list(zip(start_intervals, end_intervals))
        #pprint.pprint(interval_ranges)
        
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
    


    folder_path = r"C:\Users\nhuan\Desktop\coding-data\2022-07-08"
    for file in os.listdir(folder_path):
        file_split = file.split('-')
        if len(file_split[0]) == 1:
            file_split[0] = "0" + file_split[0]
        if len(file_split[1]) == 1:
            file_split[1] = "0" + file_split[1]
        file_split[2] = "20" + file_split[2]
        date = file_split[2] + '-' + file_split[0] + '-' + file_split[1]
        cam = file_split[4]
        part = file_split[-1].split('.')[0]
        combine_tuple = (date,cam,part)
        index = zipped_values.index(combine_tuple)
        # print(index)
        start_interval = int(start_intervals[index])
        #print(start_interval)
        end_interval = int(end_intervals[index])
        total_time = (end_interval - start_interval + 1) * 10
        # 11-17-21-H-1-WJH-ENG-MR-W
        f = os.path.join(folder_path,file)
        if os.path.isfile(f):
            print(f)
            df = pd.read_csv(f)
            unique_labels = sorted(list(df['Label'].unique()))
            times = {}
            # start_interval = int(input("start interval: "))
            # end_interval = int(input("end interval: "))
            # total_time = (end_interval - start_interval + 1) * 10
            replace_list = ["bt/peers","instructor/screen/on task"]
            df = df[(df['Interval'] >= start_interval)
                                & (df['Interval'] <= end_interval)]
            if len(unique_labels) > 1:
                df.replace(unique_labels, replace_list, inplace=True)

            fixed_labels = sorted(list(df['Label'].unique()))
            for label in fixed_labels:
                df_label = df[df['Label'] == label].copy()
                # print(df_label)
                df_label['time held'] = df_label['Time Released'] - df_label['Time Pressed'] 
                time_held = round(df_label['time held'].sum(),4)
                times[label] = time_held
            times['off target'] = round(total_time - sum(times.values()),4)

            total = sum(times.values(),0.0)
            perc = {k: round(v/total,4) for k,v in times.items()}
            print(times)
            print(perc)
            print('-----------------------------------------------------------------------------------------')
if __name__ == '__main__':
    main()















