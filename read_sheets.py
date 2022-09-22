import os.path
from turtle import heading

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

API_KEY = "AIzaSyBS4WER1pVPonoXoBD9WDjeTOZHQwM-VFA"
FOLDER_ID = "1AynxiUqO57f_TZSWzu1Dee5C8BWTQ4Iy"

drive_service = build('drive', 'v3', developerKey=API_KEY)
sheets_service = build('sheets', 'v4', developerKey=API_KEY)
sheet = sheets_service.spreadsheets()

def read_sheet(sheet_id):
    # sheet_name = "Form Responses 1"
    # sheet_object = sheet.get(spreadsheetId=sheet_id).execute()
    result = sheet.values().get(spreadsheetId=sheet_id, range="A1:BZ1000").execute()

    data = result['values']
    header = data.pop(0)
    df = pd.DataFrame(data, columns=header)
    df = df.drop(columns="Timestamp")
    # print(df)
    # print(df['Who are you?'])
    df_stacked = df.set_index('Who are you?').stack().reset_index(name='Pick').rename(columns={'level_1':'Game'})
    # print(df_stacked)
    return df_stacked

# Iterate through all sheets in folder
# response = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.spreadsheet' and trashed = false and parents in '{FOLDER_ID}'", spaces='drive', fields='nextPageToken, files(id, name)', pageToken=None).execute()
response = drive_service.files().list(q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name contains '(Responses)' and trashed = false", spaces='drive', fields='files(id, name)').execute()

all_data = []
for file in response.get('files', []):
    # print(f"Found file: {file.get('name')}, {file.get('id')}")
    all_data.append(read_sheet(file.get('id')))
df = pd.concat(all_data, axis=0)
print(df["Who are you?"].value_counts())
    


