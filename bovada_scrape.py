import requests
import pandas as pd
import time

source = requests.get("https://www.bovada.lv/services/sports/event/v2/events/A/description/football/nfl").json()
data = source[0]

# only looks 4 days ahead of time
days = 4
time_cutoff = days * 24 * 60 * 60 * 1000 

# gets current time in milliseconds
t = time.time()
t_ms = int(t * 1000)

#initializing dataframes and lists to append final data
question_form = pd.DataFrame()
matchup_list = []
start_time = []
away_odds = []
home_odds = []


#data is held in a json, need to iterate through multiple dictionaries for each game
for i in range(len(data['events'])):
    # Matchup_Name = the Away Team @ Home Team
    matchup_name = data['events'][i]
    matchup_list.append(matchup_name['description'])
    # print(matchup_name['description'])
    start_time.append(matchup_name['startTime'])
    game_data = data['events'][i]['displayGroups']
    # print(tmp)
    for j in range(len(game_data)):
        # prop_type = Game Lines, Player Props, etc.
        prop_type = game_data[j]['description']
        if prop_type == 'Game Lines':
            # all_odds = all the odds for all different types of bets for a given game
            all_odds = game_data[j]['markets']
            for k in range(len(all_odds)):
                # bet_type = Point Spread, Moneyline, etc.
                bet_type = all_odds[k]['description']
                if bet_type == 'Point Spread':
                    # time_period = Game bet, 1Q, 1H, etc. bet
                    time_period = all_odds[k]['period']['description']
                    if all_odds[k]['period']['description'] == 'Game':
                        for l in [0,1]: # 0 is Away Team odds, 1 is Home Team odds
                            if l == 0:
                                team_name_full = (all_odds[k]['outcomes'][l]['description'])
                                team_name_list = team_name_full.split()
                                team_name = team_name_list[len(team_name_list)-1]
                                spread = (all_odds[k]['outcomes'][l]['price']['handicap'])
                                if spread[0] != '-':
                                    spread = '+' + spread
                                odds = (all_odds[k]['outcomes'][l]['price']['american'])
                                if odds[0] != '-':
                                    odds = '+' + odds
                                tag = team_name + ' ' + spread + ' (' + odds + ')'
                                away_odds.append(tag)
                            else:
                                team_name_full = (all_odds[k]['outcomes'][l]['description'])
                                team_name_list = team_name_full.split()
                                team_name = team_name_list[len(team_name_list)-1]
                                spread = (all_odds[k]['outcomes'][l]['price']['handicap'])
                                if spread[0] != '-':
                                    spread = '+' + spread
                                odds = (all_odds[k]['outcomes'][l]['price']['american'])
                                tag =  team_name + ' ' + spread + ' (' + odds + ')'
                                if tag == '':
                                    tag = "N/A"
                                home_odds.append(tag)


question_form['Question'] = matchup_list
question_form['Start_Time'] = start_time
question_form['Answer 1'] = away_odds
question_form['Answer 2'] = home_odds


question_form = question_form[question_form['Start_Time'] - t_ms < time_cutoff]
question_form = question_form.drop(columns= 'Start_Time')
question_form['Type'] = 'MULTIPLE CHOICE'
question_form['Required'] = 'TRUE'
question_form.loc[-1] = ['Who are you?', '', '', 'TEXT', 'TRUE']
question_form = question_form.sort_index()

import pygsheets

#authorization
gc = pygsheets.authorize(service_file='creds.json')

#open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
sh = gc.open('Weeks Games')

#select the first sheet 
wks = sh[0]

# #update the first sheet with df, starting at cell B2. 
wks.set_dataframe(question_form,(1,1))




