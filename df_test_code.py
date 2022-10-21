from read_sheets import read_sheets
import plotly.express as px
import pandas as pd
import numpy as np

df1 = read_sheets()
json_data = df1.to_json(orient="columns")
df2 = pd.read_json(json_data, orient="columns")

df_table = df2[["Name","Correct?", "Incorrect?", "Push?", "Profit"]].copy()
df_table = df_table.groupby("Name", as_index=False).sum(numeric_only=True).sort_values(by=["Correct?", "Profit"], ascending=False)

#format profit and record
df_table["Profit"] = df_table["Profit"].apply(lambda x : f"${x:.2f}" if x>0 else f"-${-x:.2f}")
df_table["Record"] = df_table.apply(lambda x: f"{x['Correct?']}-{x['Incorrect?']}-{x['Push?']}", axis="columns")
df_table.drop(columns=["Correct?", "Incorrect?", "Push?"], inplace=True)

print(df_table[["Name", "Record", "Profit"]])