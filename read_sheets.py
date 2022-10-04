#from calendar import week
#import os.path

#from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
import pandas as pd
import re

API_KEY = "AIzaSyCH-Tgn-Hvct0UYM1QXGmo7sPbG1PFv8TE"
FOLDER_ID = "1AynxiUqO57f_TZSWzu1Dee5C8BWTQ4Iy"
ALIAS_DICT = {"Punith Upadhya": "P $hmurda", "Mr. Atticus Benjamin Ignelzi":"Atig", "Genuinely 100":"Totally 100"}
TEAM_ALIAS_DICT = {"Minnesota Vikings":"Vikings", "New Orleans Saints":"Saints", "Buffalo Bills":"Bills", "Baltimore Ravens":"Ravens", "Chicago Bears":"Bears", "New York Giants":"Giants", "Cleveland Browns":"Browns", "Atlanta Falcons":"Falcons", "Jacksonville Jaguars":"Jaguars", "Philadelphia Eagles":"Eagles", "Los Angeles Chargers":"Chargers", "Houston Texans":"Texans", "New York Jets":"Jets", "Pittsburgh Steelers":"Steelers", "Seattle Seahawks":"Seahawks", "Detroit Lions":"Lions", "Tennessee Titans":"Titans", "Indianapolis Colts":"Colts", "Washington Commanders":"Commanders", "Dallas Cowboys":"Cowboys", "Arizona Cardinals":"Cardinals", "Carolina Panthers":"Panthers", "Denver Broncos":"Broncos", "Las Vegas Raiders":"Raiders", "New England Patriots":"Patriots", "Green Bay Packers":"Packers", "Kansas City Chiefs":"Chiefs", "Tampa Bay Buccaneers":"Buccaneers", "Los Angeles Rams":"Rams", "San Francisco 49ers":"49ers"}

drive_service = build('drive', 'v3', developerKey=API_KEY)
sheets_service = build('sheets', 'v4', developerKey=API_KEY)
sheet = sheets_service.spreadsheets()

def read_sheet(sheet_id):
    result = sheet.values().get(spreadsheetId=sheet_id, range="A1:BZ1000").execute()

    #create dataframe from spreadsheet data
    data = result['values'] #list of lists
    header = data.pop(0)
    sheet_df = pd.DataFrame(data, columns=header, dtype=pd.StringDtype())
    sheet_df.dropna(axis="columns", thresh=2)
    sheet_df.dropna(axis="rows", thresh=2)
    sheet_df.drop(columns="Timestamp", inplace=True)
    
    #stack dataframe so each row is an individual bet (#rows = #people * #games)
    df_stacked = sheet_df.set_index('Who are you?').stack().reset_index(name='Pick').rename(columns={'level_1':'Game'})
    
    return df_stacked

def calc_profit(row):
    c = row["Correct?"]
    o = row["Odds"]
    a = row["Answer"]
    p = row["Push?"]
    if pd.isna(c) or pd.isna(o):
        return pd.NA
    elif a=="" or p:
        return 0
    elif not c:
        return -1
    elif o > 0:
        return o/100
    elif o < 0:
        return -100/o
    else:
        return pd.NA

def read_sheets():

    # Iterate through all sheets in folder
    # response = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.spreadsheet' and trashed = false and parents in '{FOLDER_ID}'", spaces='drive', fields='nextPageToken, files(id, name)', pageToken=None).execute()
    response = drive_service.files().list(q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name contains '(Responses)' and trashed = false", spaces='drive', fields='files(id, name)').execute()

    #read and concatenate all data from google sheets
    all_data = []
    week_num = []
    for file in response.get('files', []):
        # print(f"Found file: {file.get('name')}, {file.get('id')}")
        week_df = read_sheet(file.get('id'))
        week_num = int(re.findall(r'\d+', re.findall(r'Week \d+', file.get('name'))[0])[0]) #strip week number from pattern Week #
        week_df["Week"] = week_num
        all_data.insert(0, week_df)
    df = pd.concat(all_data, axis=0, ignore_index=True)

    #Rename "Who are you?" column to "Name"
    df.rename(columns = {'Who are you?':'Name'}, inplace = True)

    #separate home and away teams
    teams = df["Game"].str.split(" @ ", n=1, expand=True)
    df["Away"] = teams[0]
    df["Home"] = teams[1]

    #filter out just team name without location, if necessary
    df["Away"] = df["Away"].str.split(" ").str[-1]
    df["Home"] = df["Home"].str.split(" ").str[-1]


    #separate pick, spread, and odds
    picks = df["Pick"]
    picks = picks.str.replace("\(|\)", " ", regex=True) #replace parentheses with spaces
    picks = picks.str.replace("EVEN", "-100") #replace EVEN odds with -100 (mathematical equivalent)
    picks = picks.str.split(" ", n=2, expand=True)

    df["Pick"] = picks[0]
    df["Spread"] = pd.to_numeric(picks[1])
    df["Odds"] = pd.to_numeric(picks[2]) 

    #substitute known aliases
    df.replace({"Name": ALIAS_DICT}, inplace=True)

    #extract answer key from df
    answers_df = df[df["Name"]=="Answer Key"]
    df.drop(df[df["Name"]=="Answer Key"].index, inplace=True)
    answers_df = answers_df[["Game","Week","Pick"]]
    answers_df.rename(columns = {'Pick':'Answer'}, inplace = True)

    #add "Answer" and "Correct?" columns
    df = pd.merge(df, answers_df, how='left', on=['Game', 'Week'])
    df["Correct?"] = df["Pick"] == df["Answer"]

    #handle pushes
    df["Push?"] = df["Answer"].str.lower() == "push"

    #add "Profit" column normalized to $1 bet
    df["Profit"] = df.apply(calc_profit, axis="columns")

    return df
        


