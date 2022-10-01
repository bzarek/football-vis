import plotly.express as px
import dash
import pandas as pd
from read_sheets import read_sheets
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, path="/season", title="Season", name="Season")

plot_color_palette = ["#57aff2","#ae06d3","#ed872f","#e5205b","#048aa5","#2b8c0b","#4a0075","#f46b42","#236c8e",
                      "#efb42b","#bdd8fc","#b51214","#204f2a","#0aaf44","#b5b5b5","#f7d19b","#683ac4","#930d47","#cce8ff","#4caa1d","#c1682c",
                      "#6f7a8e","#DD7230","55868C","6F1D1B","#d78eed","#c9b00e","#46f4ef"]

layout = html.Div(
    children=[ 
        dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id="season_bar_chart", config={"displayModeBar":False}), width=12, md=5),
                dbc.Col(dcc.Graph(id="season_line_plot", config={"displayModeBar":False}), width=12, md=5)
                ], justify="evenly", 
                style={"margin-top":"24px"})
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

    fig_line = px.line(df_cumsum, x="Week", y="Cumulative Wins", color="Name", labels={"Cumulative Wins":"Cumulative Correct Picks"},
        color_discrete_sequence=plot_color_palette)

    fig_bar = px.bar(df_cumsum, x="Correct Picks", y="Name", color="Week String", labels={"Week String":"Week"},
        color_discrete_sequence=plot_color_palette)
    fig_bar.update_layout(yaxis=dict(autorange="reversed")) #otherwise it displays in reverse alphabetical order

    return fig_line, fig_bar