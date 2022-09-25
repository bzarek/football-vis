#import numpy as np
import pandas as pd
#import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from read_sheets import read_sheets

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])
load_figure_template("FLATLY")

server = app.server

#read google sheets and store data in browser
df = read_sheets()


# week_list = list(df["Week"].unique())
# week_list.sort()
# week_list_str = ["Week " + str(w) for w in week_list]
# week_dropdown_str = week_list_str[-1]
# week_dropdown_val = week_list[-1]

mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("This Week", href="/thisweek")),
        dbc.NavItem(dbc.NavLink("Season", href="/season"))
    ],
    brand="Football Bets",
    brand_href="/",
    color="primary",
    dark=True
)

# Layout
app.layout = html.Div(
    [
        dcc.Store(id="memory", data=read_sheets().to_json(orient="columns")),

        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        ),

        html.Div(
            children=[
                dbc.Row(navbar)
            ]
        ),

        dash.page_container
    ]
)

#update data periodically
@app.callback(Output('memory', 'data'),
              Input('interval-component', 'n_intervals'))
def update_data(n):
    return read_sheets().to_json(orient="columns")


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)