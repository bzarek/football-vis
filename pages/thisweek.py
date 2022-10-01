from ctypes import alignment
import plotly.express as px
import dash
import pandas as pd
import numpy as np
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/thisweek", title="This Week", name="This Week")

"""

Styles

"""
#mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}
style_away_text = {"text-align":"right", "margin-bottom":"2px"}
style_home_text = {"margin-bottom":"2px"}
#style_team_logo = {"height":"10%", "width":"10%"}

"""

Functions

"""

def create_game_card(away_team, home_team, away_bets, home_bets, away_spread=None, home_spread=None, away_odds=None, home_odds=None, winning_team=None):
    #handle missing spread
    if away_spread is None and home_spread is not None:
        away_spread = -home_spread
    elif away_spread is not None and home_spread is None:
        home_spread = -away_spread
    
    #handle missing odds
    if away_odds is None and home_odds is not None:
        away_odds = -220 - home_odds #-100 -> -120, -105 -> -115, -110 -> -110
    elif away_odds is not None and home_odds is None:
        home_odds = -220 - away_odds #-100 -> -120, -105 -> -115, -110 -> -110

    if away_spread is None or home_spread is None or away_odds is None or home_odds is None:
        away_text = [ 
                html.H4(away_team, style=style_away_text),
                html.P(away_bets, style=style_away_text)
            ]
        home_text = [
                html.H4(home_team),
                html.P(home_bets)
            ]
    else:
        away_text = [ 
            html.H4(away_team, style=style_away_text),
            html.P(f"{away_spread:+.1f} ({away_odds:+.0f})", style={"text-align":"right", "font-size":"12px", "margin-top":"0px"}),
            html.P(away_bets, style=style_away_text)
            ]
        home_text = [
            html.H4(home_team, style=style_home_text),
            html.P(f"{home_spread:+.1f} ({home_odds:+.0f})", style={"font-size":"12px", "margin-top":"0px"}),
            html.P(home_bets, style=style_home_text)
            ]

    #fade the team that lost
    if winning_team is not None and winning_team != "":
        if winning_team==home_team:
            home_style = dict()
            away_style = {"opacity":"0.3"}
        else:
            home_style = {"opacity":"0.3"}
            away_style = dict()
    else:
        home_style = dict()
        away_style = dict()
    
    card = dbc.Card([
        dbc.Row([
            dbc.Col(
                dbc.CardBody(away_text), width=4, style=away_style
            ),
            dbc.Col(
                dbc.CardImg(src=f"/assets/images/{away_team}.png"), width=2, md=1, style=away_style
            ),
            dbc.Col(
                dbc.CardImg(src=f"/assets/images/{home_team}.png"), width=2, md=1, style=home_style
            ),
            dbc.Col(
                dbc.CardBody(home_text), width=4, style=home_style
            )
        ], 
        justify="center",
        align="center")
    ])

    return dbc.Row(card, style={"margin-bottom":"14px"})

def create_week_cards(df, week_num):

    card_list = [] #list for storing dbc.Card elements
    games_list = df[df["Week"]== week_num]["Game"].unique()

    for game in games_list:
        game_df = df[df["Game"]==game]

        #get team names
        away_team = game_df["Away"].iloc[0]
        home_team = game_df["Home"].iloc[0]
        winning_team = game_df["Answer"].iloc[0]
        print(winning_team)

        #return string of people who bet on each team (comma separated)
        #note: join will concatenate the strings in the list with ", " as the delimiter
        away_bets = ", ".join(list(game_df[df["Pick"]==away_team]["Name"]))
        home_bets = ", ".join(list(game_df[df["Pick"]==home_team]["Name"]))

        #get spread
        away_spread = game_df[df["Pick"]==away_team]["Spread"].unique()
        away_spread = None if np.size(away_spread)==0 else float(away_spread[0])
        home_spread = game_df[df["Pick"]==home_team]["Spread"].unique()
        home_spread = None if np.size(home_spread)==0 else float(home_spread[0])

        #get odds
        away_odds = game_df[df["Pick"]==away_team]["Odds"].unique()
        away_odds = None if np.size(away_odds)==0 else float(away_odds[0])
        home_odds = game_df[df["Pick"]==home_team]["Odds"].unique()
        home_odds = None if np.size(home_odds)==0 else float(home_odds[0])

        #get winning team

        card_list.append(create_game_card(away_team, home_team, away_bets, home_bets, away_spread, home_spread, away_odds, home_odds, winning_team))

    return card_list


""""

LAYOUT

"""

layout = html.Div(
    children=[ 
        dbc.Container([
            dbc.Row([
                dbc.Col(width=1),
                dbc.Col(dcc.Dropdown(id="week_dropdown", searchable=False, clearable=False), width=10, md=2,lg=1), 
                ], style={"margin-top":"24px"}), 
            dbc.Row([
                dbc.Col(dcc.Graph(id="week_total_plot", config={"displayModeBar":False}), width=12, md=8),
                ], justify="center", style={"margin-bottom":"14px"}),
            html.Div(id="game_cards")
            ], fluid=True)
        ]
    )


"""

Callbacks

"""
@callback(
    Output("week_dropdown", "options"),
    Output("week_dropdown", "value"),
    Input("memory", "data")
    )
def new_data(data):
    #extract dataframe from json
    df = pd.read_json(data, orient="columns")

    #extract valid weeks
    week_list = list(df["Week"].unique())
    week_list.sort()
    week_list_str = ["Week " + str(w) for w in week_list]
    week_dropdown_str = week_list_str[-1]

    return week_list_str, week_dropdown_str

@callback(
    Output("week_total_plot", "figure"), 
    Output("game_cards", "children"),
    State("memory", "data"),
    Input("week_dropdown", "value")
    )
def update_week(data, week_dropdown_str):
    #extract week number as an int
    week_dropdown_val = int(week_dropdown_str.split(" ")[1])

    #extract dataframe from json
    df = pd.read_json(data, orient="columns")

    #return outputs
    thisweek_df = df[df["Week"]==week_dropdown_val].groupby("Name").sum(numeric_only=True)
    fig = px.bar(thisweek_df, y="Correct?", labels={"Correct?":"Correct Picks"})
    cards = create_week_cards(df, week_dropdown_val)
    return fig, cards