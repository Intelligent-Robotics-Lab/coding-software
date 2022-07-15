from __future__ import print_function
from datetime import date

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from itertools import chain
import io

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.readonly","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.activity"]

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
    date_wanted = input("Enter date wanted (YYYY-MM-DD): ")
    date_wanted_split = date_wanted.split('-')
    date_wanted_split[-1] = str(int(date_wanted_split[-1]) - 1)
    first_date = "-".join(date_wanted_split)
    date_before_wanted = 'modifiedTime > ' + "'" + first_date + "T23:00:00'"
    query_name = 'modifiedTime < ' + "'" + date_wanted + "T23:00:00'" + ' and ' + date_before_wanted + ' and mimeType = ' + "'text/csv'"
    #print(query_name)
    folder_path = r"C:\Users\Clinic\Desktop\grab-data" + "\\" + date_wanted
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=30, fields="nextPageToken, files(id, name)", corpora='user', q=query_name, spaces='drive').execute()
        items = results.get('files', [])
        
        if not items:
            print('No files found.')
            return
        print('Number of files added: ' + str(len(items)))
        for item in items:
            file_id = item['id']
            file_name = item['name']
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(folder_path + "\\" + file_name,'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))
            print(file_name + '\t' + date_wanted + '\t' + "file id: " + file_id)
            # print(u'{0} ({1})'.format(item['name'], item['id']))
        

        
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
    



if __name__ == '__main__':
    main()