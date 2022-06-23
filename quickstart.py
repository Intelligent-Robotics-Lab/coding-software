from __future__ import print_function
from msilib.schema import ComboBox

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
import pprint as pprint
import datetime
import os


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.activity", "https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.readonly"]


def main():
    """Shows basic usage of the Drive Activity API.

    Prints information about the last 10 events that occured the user's Drive.
    """
    import time as t
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

    service = build('driveactivity', 'v2', credentials=creds)
    service_drive = build('drive','v3', credentials=creds)
    date_wanted = input("Enter in date (YYYY-MM-DD): ")
    # date_wanted_split = date_wanted.split('-')
    # date_wanted_dt = datetime.date(int(date_wanted_split[0]),int(date_wanted_split[1]),int(date_wanted_split[2]))
    # date_wanted_ut = t.mktime(date_wanted_dt.timetuple())
    # date_wanted_next_ut = date_wanted_ut + (24*3600)
    folder_path = r"C:\Users\nhuan\Desktop\coding-data" + "\\" + date_wanted
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # today = date.today().strftime("%Y-%m-%d")
    # print(today)
    # print(type(today))
    # Call the Drive Activity API
    try:
        results = service.activity().query(body={
            'pageSize': 7,
            "ancestorName": "items/1w62nXda-DNUfRBYZlD9MdXIDIDtoR3-r"
        }).execute()
        activities = results.get('activities', [])
        #pprint.pprint(activities)
        # print(len(activities))
        if not activities:
            print('No activity.')
        else:
            print('Recent activity:')
            for activity in activities:
                time = getTimeInfo(activity)
                date_added = time.split('T')[0]
                #action = getActionInfo(activity['primaryActionDetail'])
                #actors = map(getActorInfo, activity['actors'])
                targets = map(getTargetInfo, activity['targets'])
                csv_targets = map(get_csv,activity['targets'])
                file_ids = map(get_file_id,activity['targets'])
                mime_types = map(get_mime_types,activity['targets'])
                zip_list = list(zip(csv_targets,file_ids,mime_types))
                # actors_str, targets_str, csv_str = "", "", ""
                #actor_name = actors_str.join(actors)
                # target_name = targets_str.join(targets)
                # csv_name= csv_str.join(csv_targets)
                # for file_type in csv_targets:
                #     str_file_type = str(file_type)
                #     if str_file_type != 'not csv':
                #         print(str_file_type + '\t' + date_added + "file id: " + str(file_))
                
                for comb in zip_list:
                    if date_added != date_wanted:
                        continue
                    file_name = comb[0]
                    file_id = comb[1]
                    mime_type = comb[2]
                    if mime_type != 'text/csv':
                        continue
                    else:
                        request = service_drive.files().get_media(fileId=file_id)
                        fh = io.FileIO(folder_path + "\\" + file_name,'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print ("Download %d%%." % int(status.progress() * 100))
                        print(file_name + '\t' + date_added + '\t' + "file id: " + file_id)
                # Print the action occurred on drive with actor, target item and timestamp
                #print(u'{0}: {1}, {2}, {3}'.format(time, action, actor_name, target_name))
                #print(target_name)
                # print(csv_name)

    except HttpError as error:
        # TODO(developer) - Handleerrors from drive activity API.
        print(f'An error occurred: {error}')


# Returns the name of a set property in an object, or else "unknown".
def getOneOf(obj):
    for key in obj:
        return key
    return 'unknown'


# Returns a time associated with an activity.
def getTimeInfo(activity):
    if 'timestamp' in activity:
        return activity['timestamp']
    if 'timeRange' in activity:
        return activity['timeRange']['endTime']
    return 'unknown'


# Returns the type of action.
def getActionInfo(actionDetail):
    return getOneOf(actionDetail)


# Returns user information, or the type of user if not a known user.
def getUserInfo(user):
    if 'knownUser' in user:
        knownUser = user['knownUser']
        isMe = knownUser.get('isCurrentUser', False)
        return u'people/me' if isMe else knownUser['personName']
    return getOneOf(user)


# Returns actor information, or the type of actor if not a user.
def getActorInfo(actor):
    if 'user' in actor:
        return getUserInfo(actor['user'])
    return getOneOf(actor)

def get_mime_types(target):
    if 'driveItem' in target:
        mime_type = target['driveItem']['mimeType']
        return mime_type
    return ""
def get_file_id(target):
    if 'driveItem' in target:
        file_id_path = target['driveItem']['name']
        file_id = file_id_path.split('/')[1]
        return file_id
    return 'unknown id'

# Returns the type of a target and an associated title.
def get_csv(target):
    if 'driveItem' in target:
        mime_type = target['driveItem']['mimeType']
        if mime_type == 'text/csv':
            title = target['driveItem'].get('title','unknown')
            return title
    return 'not csv'

def getTargetInfo(target):
    if 'driveItem' in target:
        title = target['driveItem'].get('title', 'unknown')
        # print(target['driveItem']['mimeType'])
        return 'driveItem:"{0}"'.format(title)
    if 'drive' in target:
        title = target['drive'].get('title', 'unknown')
        return 'drive:"{0}"'.format(title)
    if 'fileComment' in target:
        parent = target['fileComment'].get('parent', {})
        title = parent.get('title', 'unknown')
        return 'fileComment:"{0}"'.format(title)
    return '{0}:unknown'.format(getOneOf(target))


if __name__ == '__main__':
    main()



