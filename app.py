#import numpy as np
from textwrap import indent
import pandas as pd
#import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from db.read_sheets import read_sheets
import json

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.MATERIA])
load_figure_template("MATERIA")

server = app.server

#read data from Google Sheets
try:
    with open("/app/db/data/datatable.json", "r") as infile:
        sheets_data = json.load(infile)
except:
    sheets_data = read_sheets(to_json=True, json_path="/app/db/data/datatable.json")

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("This Week", href="/thisweek", active="exact")),
        dbc.NavItem(dbc.NavLink("Season", href="/season", active="exact"))
    ],
    pills=True,
    justified=True
)

# Layout
app.layout = html.Div(
    [
        dcc.Store(id="memory", data=sheets_data),

        dcc.Interval(
            id='interval-component',
            interval=5*60*1000, # in milliseconds
            n_intervals=0
        ),

        html.Div(
            children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col(navbar, width=12, md=4),
                    ], justify="center")
                    ], fluid=True
                    )
                ]
            ),

        dash.page_container
        ]
    )

#update data periodically (also updates on refresh when interval component gets reset)
# @app.callback(Output('memory', 'data'),
#               Input('interval-component', 'n_intervals'))
# def update_data(n):
#     try:
#         with open("db/datatable.json", "r") as infile:
#             return json.load(infile)
#     except:
#         return read_sheets(to_json=True, json_path="datatable.json").to_json(orient="columns")
    # return read_sheets().to_json(orient="columns")

#update data periodically (also updates on refresh when interval component gets reset)
@app.callback(Output('memory', 'data'),
              Input('interval-component', 'n_intervals'))
def update_data(n):
    try:
        with open("/app/db/data/datatable.json", "r") as infile:
            sheets_data = json.load(infile)
    except:
        sheets_data = read_sheets(to_json=True, json_path="/app/db/data/datatable.json")
    return sheets_data

# Run local server
if __name__ == '__main__':
    app.run_server(debug=False)