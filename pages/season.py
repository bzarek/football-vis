import plotly.express as px
import dash
import pandas as pd
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/season", title="Season", name="Season")

mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

layout = html.Div(
    children=[ 
        dbc.Row([
            dbc.Col(width=1),
            dbc.Col(dcc.Graph(id="season_line_plot", config={"displayModeBar":False}), style=mystyle, width=10),
            dbc.Col(width=1)
            ])
        ]
    )

# Callbacks

@callback(
    Output("season_line_plot", "figure"), 
    Input("memory", "data"),
    )
def new_data(data):

    #extract dataframe from json
    df = pd.read_json(data, orient="columns")

    #return outputs
    thisweek_df = df.groupby(["Name", "Week"]).sum(numeric_only=True)
    fig = px.line(thisweek_df, y="Correct?", labels={"Name", "Correct Picks"})
    return fig