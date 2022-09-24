import plotly.express as px
import dash
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/thisweek", title="This Week", name="This Week")

mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

df = read_sheets()

week_list = list(df["Week"].unique())
week_list.sort()
week_list_str = ["Week " + str(w) for w in week_list]
week_dropdown_str = week_list_str[-1]
week_dropdown_val = week_list[-1]

layout = html.Div(
    children=[
        dbc.Row(html.H1(children="This Week"), style=mystyle), 
        dbc.Row([
            dbc.Col(dcc.Dropdown(options=week_list_str, value=week_list_str[-1], id="week_dropdown"), style=mystyle, width=3), 
            dbc.Col()
            ]), 
        dbc.Row(dcc.Graph(id="week_total_plot"), style=mystyle)
        ]
    )

# Callbacks
@callback(
    Output("week_total_plot", "figure"), 
    Input(component_id="week_dropdown", component_property="value")
    )
def update_week(week_dropdown_str):
    week_dropdown_val = int(week_dropdown_str.split(" ")[1])

    fig = px.bar(df[df["Week"]==week_dropdown_val].groupby("Name").sum(numeric_only=True), y="Correct?")
    return fig 