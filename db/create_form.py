from urllib.request import urlopen
import json
import os
import argparse
import time
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from discord import SyncWebhook

WEEK1_EPOCH_MS = 1662508801000

FOLDER_ID = "1AynxiUqO57f_TZSWzu1Dee5C8BWTQ4Iy"
bovada_url = "https://www.bovada.lv/services/sports/event/v2/events/A/description/football/nfl"

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

GOOGLE_CRED_DIR = "/app/football-vis-e903da22c051.json"
credentials = service_account.Credentials.from_service_account_file(filename=GOOGLE_CRED_DIR)

form_service = build('forms', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

#helper functions

def delete_question(index):
    return {
        "requests": [{
            "deleteItem": {
                "location": {
                    "index": index
                }
            }
        }]
    }

def create_game_question(home_team, home_spread, home_odds, away_team, away_spread, away_odds, question_index):
    #isolate team name without location, if necessary
    home_team = home_team.split(" ")[-1]
    away_team = away_team.split(" ")[-1]

    matchup = f"{away_team} @ {home_team}"
    option1 = f"{away_team} {float(away_spread):+.1f} ({away_odds})"
    option2 = f"{home_team} {float(home_spread):+.1f} ({home_odds})"

    new_question = {
        "requests": [{
            "createItem": {
                "item": {
                    "title": matchup,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": option1},
                                    {"value": option2}
                                ],
                                "shuffle": False
                            }
                        }
                    },
                },
                "location": {
                    "index": question_index
                }
            }
        }]
    }
    return new_question

def create_name_question():
    new_question = {
        "requests": [{
            "createItem": {
                "item": {
                    "title": "Who are you?",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {
                                "paragraph": False
                            }
                        }
                    },
                },
                "location": {
                    "index": 0
                }
            }
        }]
    }
    return new_question

def create_new_form(week_num):
    #auto-increment the # of the form
    #e.g. "Week 1 - NFL Betting #1", "Week 1 - NFL Betting #2", etc.
    iter_num = 0
    file_found = True
    while file_found:
        iter_num = iter_num + 1
        form_name = f"Week {week_num} - NFL Betting #{iter_num}"
        search_query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.form' and name contains '{form_name}' and trashed = false"
        response = drive_service.files().list(q=search_query, spaces='drive', fields='files(id, name)').execute()
        file_found = len(response["files"]) > 0

    file_metadata = {
            'name': form_name,
            'mimeType': 'application/vnd.google-apps.form',
        }

    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    
    #move file
    parent_data = drive_service.files().get(fileId=file["id"], fields='parents').execute()
    previous_parents = ",".join(parent_data.get('parents'))
    file = drive_service.files().update(fileId=file["id"], addParents=FOLDER_ID, removeParents=previous_parents, fields='id, parents').execute()

    #delete blank question that is created by default
    form_service.forms().batchUpdate(formId=file["id"], body=delete_question(0)).execute() 

    return file

#main function

def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", help="number of days into the future to pull football games", type=int, default=3)
    args = parser.parse_args()
    days = int(args.days)

    #get the current time and the number of weeks that have passed since first game
    current_time_ms = time.time() * 1000
    week_num = int((datetime.datetime.utcfromtimestamp(current_time_ms/1000) - datetime.datetime.utcfromtimestamp(WEEK1_EPOCH_MS/1000)).days/7)+1

    #create initial form
    result = create_new_form(week_num)

    #create name question
    form_service.forms().batchUpdate(formId=result["id"], body=create_name_question()).execute()

    #get list of upcoming games
    response = urlopen(bovada_url)
    game_list = json.loads(response.read())[0]["events"]

    #set cutoff time in ms since epoch
    cutoff_time_ms = current_time_ms + days*24*60*60*1000
    
    #begin question index at 2 (Who are you? question is number 1)
    question_index = 1

    for game in game_list: #iterate over games
        if game["startTime"] > current_time_ms and game["startTime"] < cutoff_time_ms: #only consider games within certain time window
            
            #iterate through unordered lists to find game lines and point spread
            #stop once the right info is found
            for group in game["displayGroups"]: 
                if group["description"] == "Game Lines":
                    for market in group["markets"]:
                        if market["description"] == "Point Spread" and market["period"]["description"] == "Game": #then this is what we're looking for
                            home_team = market["outcomes"][1]["description"]
                            home_spread = market["outcomes"][1]["price"]["handicap"]
                            home_odds = market["outcomes"][1]["price"]["american"] #american odds
                            away_team = market["outcomes"][0]["description"]
                            away_spread = market["outcomes"][0]["price"]["handicap"]
                            away_odds = market["outcomes"][0]["price"]["american"] #american odds
                            form_service.forms().batchUpdate(formId=result["id"], body=create_game_question(home_team, home_spread, home_odds, away_team, away_spread, away_odds, question_index)).execute()
                            question_index = question_index + 1
                            break #exit out of this loop now what we've found what we're looking for
                break #exit out of this loop now what we've found what we're looking for

    #post link on discord server
    form_response_url = form_service.forms().get(formId=result["id"]).execute()["responderUri"]
    discord_webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
    discord_webhook.send(form_response_url)


    



if __name__ == "__main__":
    __main__()
