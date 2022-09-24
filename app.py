import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from read_sheets import read_sheets

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.MATERIA])
load_figure_template("MATERIA")

server = app.server

# df = read_sheets()

# week_list = list(df["Week"].unique())
# week_list.sort()
# week_list_str = ["Week " + str(w) for w in week_list]
# week_dropdown_str = week_list_str[-1]
# week_dropdown_val = week_list[-1]

mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

# Layout
app.layout = html.Div([
    html.Div(),

    dash.page_container
    ])







# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)