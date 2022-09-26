import plotly.express as px
import dash
import pandas as pd
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/season", title="Season", name="Season")

#mystyle = {"margin-left":"7px", "margin-top":"7px", "margin-right":"7px"}

layout = html.Div(
    children=[ 
        dbc.Container([
            dbc.Row([
                dbc.Col(width=1),
                dbc.Col(dcc.Graph(id="season_bar_chart", config={"displayModeBar":False}), width=5),
                dbc.Col(dcc.Graph(id="season_line_plot", config={"displayModeBar":False}), width=5),
                dbc.Col(width=1)
                ], style={"margin-top":"24px"})
            ], fluid=True)
        ]
    )

# Callbacks

@callback(
    Output("season_line_plot", "figure"), 
    Output("season_bar_chart", "figure"),
    Input("memory", "data"),
    )
def new_data(data):

    #extract dataframe from json
    df = pd.read_json(data, orient="columns")

    df_cumsum = df[["Name", "Week", "Correct?"]].copy()
    df_cumsum.rename(columns={"Correct?":"Correct Picks"}, inplace=True)
    df_cumsum = df_cumsum.groupby(["Name","Week"], as_index=False).sum(numeric_only=True).sort_values(["Name","Week"]).copy()
    df_cumsum["Cumulative Wins"] = df_cumsum.groupby("Name")["Correct Picks"].transform(pd.Series.cumsum)
    df_cumsum["Week String"] = "Week " + df_cumsum["Week"].astype("string")

    fig_line = px.line(df_cumsum, x="Week", y="Cumulative Wins", color="Name", labels={"Cumulative Wins":"Cumulative Correct Picks"})
    fig_bar = px.bar(df_cumsum, x="Correct Picks", y="Name", color="Week String", labels={"Week String":"Week"})
    fig_bar.update_layout(yaxis=dict(autorange="reversed")) #otherwise it displays in reverse alphabetical order

    return fig_line, fig_bar