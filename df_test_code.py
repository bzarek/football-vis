from read_sheets import read_sheets
import plotly.express as px


df = read_sheets()
df_processed = df[df["Week"]==1].groupby("Name").sum(numeric_only=True)

px.bar(df_processed, y="Correct?", labels={"Name", "Correct Picks"}).show()