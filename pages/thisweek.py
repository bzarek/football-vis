import plotly.express as px
import dash
import pandas as pd
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/thisweek", title="This Week", name="This Week")

#mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

layout = html.Div(
    children=[ 
        dbc.Container([
            dbc.Row([
                dbc.Col(width=1),
                dbc.Col(dcc.Dropdown(id="week_dropdown", searchable=False, clearable=False), width=1, ), 
                dbc.Col()
                ], style={"margin-top":"24px"}), 
            dbc.Row([
                dbc.Col(width=1),
                dbc.Col(dcc.Graph(id="week_total_plot", config={"displayModeBar":False}), width=10),
                dbc.Col()
                ])
            ], fluid=True)
        ]
    )

# Callbacks
@callback(
    Output("week_dropdown", "options"),
    Output("week_dropdown", "value"),
    Input("memory", "data"),
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
    return fig