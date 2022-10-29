#from calendar import week
from ast import arg
import os
import argparse

#from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
import pandas as pd
import re
import json 
import time

API_KEY = os.environ["GOOGLE_API_KEY"]
FOLDER_ID = "1AynxiUqO57f_TZSWzu1Dee5C8BWTQ4Iy"
ALIAS_DICT = {"Punith Upadhya": "P $hmurda", "Punith":"P $hmurda", "Mr. Atticus Benjamin Ignelzi":"Atig", "Genuinely 100":"Totally 100"}
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
    i = row["Incorrect?"]
    o = row["Odds"]
    a = row["Answer"]
    p = row["Push?"]
    if pd.isna(c) or pd.isna(o):
        return pd.NA
    elif pd.isna(a) or a=="" or p:
        return 0
    elif i:
        return -1
    elif o > 0:
        return o/100
    elif o < 0:
        return -100/o
    else:
        return pd.NA

def read_sheets(to_json=False, json_path="data/datatable.json", read_all=False):

    #check when we last updated the json and add it to the search query
    if to_json and not read_all:
        try:
            json_modify_date = os.path.getmtime(json_path)
        except:
            json_modify_date = 0 #epoch
        #now include this in search query
        json_modify_date_str = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(json_modify_date))
        search_query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name contains '(Responses)' and trashed = false and modifiedTime > '{json_modify_date_str}'"
        # search_query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' \
        #                                 and name contains '(Responses)' and trashed = false"
    else: #want to read all files if not using a json file
        search_query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name contains '(Responses)' and trashed = false"

    # Iterate through all sheets in folder
    # response = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.spreadsheet' and trashed = false and parents in '{FOLDER_ID}'", spaces='drive', fields='nextPageToken, files(id, name)', pageToken=None).execute()
    response = drive_service.files().list(q=search_query, spaces='drive', fields='files(id, name)').execute()

    #read and concatenate all data from google sheets
    all_data = []
    week_num = []
    for file in response.get('files', []):
        print(file)
        print("here's a file")
        # print(f"Found file: {file.get('name')}, {file.get('id')}")
        week_df = read_sheet(file.get('id'))
        week_num = int(re.findall(r'\d+', re.findall(r'Week \d+', file.get('name'))[0])[0]) #strip week number from pattern Week #
        week_df["Week"] = week_num
        all_data.insert(0, week_df)
    
    if not all_data and to_json: #this means all_data is empty (no sheets read)
        with open(json_path, "r") as infile:
            sheets_data = json.load(infile)
        return sheets_data #just return the existing data
        
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
    
    #add boolean columns for Correct, Incorrect, and Push
    df["Correct?"] = df["Pick"] == df["Answer"] 
    df["Push?"] = df["Answer"].str.lower() == "push"
    df["Incorrect?"] = ~df["Correct?"] & ~df["Push?"] #relies on Correct? column containing NA values for missing data

    #fill missing booleans with False to avoid inconsistent behavior
    df["Push?"] = df["Push?"].fillna(False)
    df["Correct?"] = df["Correct?"].fillna(False)
    df["Incorrect?"] = df["Incorrect?"].fillna(False)

    #add "Profit" column normalized to $1 bet
    df["Profit"] = df.apply(calc_profit, axis="columns")

    
    if to_json:
        try:
            #handle updated data (make sure there are no duplicates)
            df_stored = pd.read_json(json_path)
            df_concat = pd.concat([df_stored, df], axis=0, ignore_index=True).drop_duplicates(subset=["Name", "Game"], keep="last")
        except:
            df_concat = df

        #Write to JSON file, creating directory if necessary
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as outfile:
            json.dump(df_concat.to_json(orient="columns"), outfile)

    return df.to_json(orient="columns")

#definition for executing read_sheets() from command line using command line arguments
def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to json file", default="data/datatable.json")
    parser.add_argument("--fullread", action="store_true", help="read all data from Google Drive folder, regardless of modify date")
    args = parser.parse_args()
    # print(type(args.path))
    # print(args.fullread)
    read_sheets(to_json=True, json_path=args.path, read_all=args.fullread)

if __name__ == "__main__":
    __main__()