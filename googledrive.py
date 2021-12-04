from __future__ import print_function
import httplib2
import os, io
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Applicaction name'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'app_api_key.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = build('drive', 'v3', http=http)


def download_document(id, path, mtype):
    request = service.files().export_media(fileId=id, mimeType=mtype)
    fh = io.FileIO(path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def download_file(id, path):
    request = service.files().get_media(fileId=id)
    fh = io.FileIO(path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def main():
    files = service.files().list(fields='files(name, id, mimeType)').execute().get('files')
    items = [[], [], []]
    for item in files:
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            items[0].append(item['id'])
            items[1].append(item['name'])
            items[2].append(item['mimeType'])
    return items


if __name__ == '__main__':
    main()
