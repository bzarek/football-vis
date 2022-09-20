import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

app = Dash()

server = app.server

power_dropdown = dcc.Dropdown(options=["One", "Two", "Three", "Four"], value="One")

app.layout = html.Div(children=[html.H1(children="Test Dashboard"), power_dropdown, dcc.Graph(id="poly_plot")])

@app.callback(Output(component_id="poly_plot", component_property="figure"), Input(component_id=power_dropdown, component_property="value"))
def update_graph(power):
    if power == "One":
        power_int = 1
    elif power == "Two":
        power_int = 2
    elif power == "Three":
        power_int = 3
    else:
        power_int = 4
    
    x = np.linspace(0,10)
    y = x**power_int
    df = pd.DataFrame(np.stack([x,y],1), columns=["x", "y"])
    
    fig = px.line(df, x="x", y="y", title=f"Polynomial Function y=x^{power_int}")
    return fig 

# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)


# fig.show()
# df.info()
# print(df["x"].value_counts())