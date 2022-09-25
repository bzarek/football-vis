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
                dbc.Col(width=1),
                dbc.Col(html.Div(id="container_leaderboard"), width=10), 
                dbc.Col(width=1)
                ], style={"margin-top":"24px"})
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

    #return table
    df_table = df[["Name","Correct?", "Profit"]].copy()
    df_table.rename(columns={"Correct?":"Correct Picks"}, inplace=True) #change column name for display purposes
    df_table = df_table.groupby("Name", as_index=False).sum(numeric_only=True).sort_values(by=["Correct Picks", "Profit"], ascending=False)
    df_table["Profit"] = df_table["Profit"].apply(lambda x : f"${x:.2f}" if x>0 else f"-${-x:.2f}")
    return dbc.Table.from_dataframe(
        df_table
        )