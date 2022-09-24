import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/", title="Home", name="Home")

mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

layout = html.Div(children=[html.H1(children="Leaderboard")], style=mystyle)