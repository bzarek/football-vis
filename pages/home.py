from numpy import size
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd

dash.register_page(__name__, path="/", title="Home", name="Home")

#mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

layout = html.Div(
    children=[ 
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div(id="container_leaderboard"), width=12, md=3), 
                ], justify="center",
                style={"margin-top":"24px"})
            ], fluid=True)
        ]
    )

@callback(
    Output("container_leaderboard", "children"), 
    Input("memory", "data"),
    )
def new_data(data):

    #extract dataframe from json
    df = pd.read_json(data, orient="columns")

    #create table with sums by name
    df_table = df[["Name","Correct?", "Incorrect?", "Push?", "Profit"]].copy()
    df_table = df_table.groupby("Name", as_index=False).sum(numeric_only=True).sort_values(by=["Correct?", "Profit"], ascending=False)

    #format profit and record
    df_table["Profit"] = df_table["Profit"].apply(lambda x : f"${x:.2f}" if x>0 else f"-${-x:.2f}")
    df_table["Record"] = df_table.apply(lambda x: f"{x['Correct?']} - {x['Incorrect?']} - {x['Push?']}", axis="columns")
    df_table.drop(columns=["Correct?", "Incorrect?", "Push?"], inplace=True)

    return dbc.Table.from_dataframe(
        df_table[["Name", "Record", "Profit"]]
        )