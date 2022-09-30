from ctypes import alignment
import plotly.express as px
import dash
import pandas as pd
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/thisweek", title="This Week", name="This Week")

"""

Styles

"""
#mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}
style_away_text = {"text-align":"right"}
#style_team_logo = {"height":"10%", "width":"10%"}

"""

Functions

"""

def create_game_card(away_team, home_team, away_bets, home_bets, away_spread=None, home_spread=None, away_odds=None, home_odds=None):
    card = dbc.Card([
        dbc.Row([
            dbc.Col(
                dbc.CardBody([ 
                    html.H4(away_team, style=style_away_text),
                    html.P(away_bets, style=style_away_text),
                ])
            ),
            dbc.Col(
                dbc.CardImg(src=f"/assets/images/{away_team}.png"), md=1
            ),
            dbc.Col(
                dbc.CardImg(src=f"/assets/images/{home_team}.png"), md=1
            ),
            dbc.Col(
                dbc.CardBody([ 
                    html.H4(home_team),
                    html.P(home_bets),
                ])
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

        #return string of people who bet on each team (comma separated)
        #note: join will concatenate the strings in the list with ", " as the delimiter
        away_bets = ", ".join(list(game_df[df["Pick"]==away_team]["Name"]))
        home_bets = ", ".join(list(game_df[df["Pick"]==home_team]["Name"]))

        card_list.append(create_game_card(away_team, home_team, away_bets, home_bets))

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