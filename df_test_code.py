from read_sheets import read_sheets
import plotly.express as px
import pandas as pd


df = read_sheets()
df_reduced = df[["Name", "Week", "Correct?"]].copy()
df_reduced.rename(columns={"Correct?":"Correct Picks"}, inplace=True)
df_organized = df_reduced.groupby(["Name","Week"], as_index=False).sum(numeric_only=True).sort_values(["Name","Week"]).copy()
df_organized["Cumulative Wins"] = df_organized.groupby("Name")["Correct Picks"].transform(pd.Series.cumsum)

#print(df)
#print(df_reduced)
print(df_organized)

#px.bar(df_processed, y="Correct?", labels={"Name", "Correct Picks"}).show()