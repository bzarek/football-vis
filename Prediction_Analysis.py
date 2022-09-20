from calendar import week
from http.client import responses
from pathlib import Path
from skimage.io import imread, imsave
from skimage.util import img_as_ubyte
from skimage.filters import gaussian
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

def main():
    week = str("Week 2")
    df = get_data()
    answers, responses = answer_key(df)
    pick_viz(responses)
    correct, incorrect = check_answers(answers, responses)
    correct_viz(correct)
    aggregate_data(correct, week)
    per_week_performance(week)
    


def get_data():
    path = r'A:\David Yeh\Documents\Documents\Data Analytics\Football_Predictions\Week 2\Week 2 - NFL Betting (Responses).xlsx'
    df = pd.read_excel(path)
    return df


def answer_key(df):
    answer_key_val = df[df["Who are you?"] == "Answer Key"]
    responses = df[df["Who are you?"] != "Answer Key"]
    consensus = []
    for i in range(len(responses.columns)):
        if i == 0:
            consensus.append("N/A")
        elif i == 1:
            consensus.append("Consensus")
        else:
            tmp = (responses.iloc[:,i].mode()).to_string(index = False)
            tmp = tmp[1:len(tmp)]
            consensus.append(tmp)
    responses.loc[len(responses)] = consensus
    return(answer_key_val, responses)

def pick_viz(val):
    headers = list(val.columns)
    overall_df = pd.DataFrame()
    val = val[val["Who are you?"] != "Consensus"]
    for i in range(2, len(val.columns)):
        tmp = val.iloc[:,i]
        tmp_header = headers[i]
        tmp_header = tmp_header.split()
        home = tmp_header[2]
        home_count = 0
        away_count = 0
        for j in range(len(tmp)):
            tmp_vl = tmp[j]
            if home in tmp_vl:
                home_count += 1
            else:
                away_count += 1
        tmp_d = {"Game" : headers[i], "Home" : home_count, "Away" : away_count}
        overall_df=overall_df.append(tmp_d, ignore_index= True)


    plt.rcParams.update({'font.size': 10})
    overall_df.plot(kind='bar',
                x = "Game", 
                stacked=True, 
                color = ['#D63D1D', '#1EB2E4'], 
                figsize=(10, 6))

    plt.legend(loc="upper left", ncol=2)
    plt.xlabel("Game")
    plt.ylabel("Picks")
    plt.tight_layout()
    plt.show()

def check_answers(answer, response):

    correct = {}
    incorrect = {}
    answer = answer.reset_index()
    answer_val = answer.iloc[0,:]
    answer_set = set(answer_val)


    for i in range(len(response)):
        b_set = set(response.iloc[i,:])
        name = response.iloc[i, 1]
        correct[name] = len(answer_set.intersection(b_set))
        incorrect[name] = (answer_set - b_set)
    print(correct)
    return correct, incorrect

def correct_viz(data):
    name = list(data.keys())
    val = list(data.values())
    plt.bar(range(len(data)), val, tick_label=name)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()

def aggregate_data(data, week):
    data = pd.DataFrame(data.items())
    data.to_excel(r'A:\\David Yeh\\Documents\\Documents\\Data Analytics\\Football_Predictions' + "\\" + week + "_aggregated" + ".xlsx")

def per_week_performance(week):
    path = r'A:\David Yeh\Documents\Documents\Data Analytics\Football_Predictions\Total_Aggregated_Data.xlsx'
    df = pd.read_excel(path, index_col=[0])
    # df[week, :] = 
    print(df)
    for i in range(1, len(df)):
        tmp = "Week " + str(i+1)
        tmp_2 = "Week " + str(i)
        for j in df.columns:
            df.loc[tmp, j] = df.loc[tmp_2, j] + df.loc[tmp, j]
    lines = df.plot.line()
    plt.ylabel("# of Picks Correct")
    plt.show(lines)
    
    
    


if __name__ == "__main__":
    main()