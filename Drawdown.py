import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as datetime

df = pd.read_csv('historicalReturns.csv')

new_header = df.iloc[0] #grab the first row for the header
df = df[1:] #take the data less the header row
df.columns = new_header #set the header row as the df header
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

def rebase(df):
    for i in range(len(df.columns.values.tolist())-1):
        changed = 0
        for rows in range(len(df)):
            if changed == 1:
                df.iloc[rows,i] = df.iloc[rows-1,i] + df.iloc[rows-1,i] * float(df.iloc[rows,i])/100
            if changed == 0:
                if type(df.iloc[rows,i]) == str:
                    df.iloc[rows,i] = float(100)
                    changed = 1
                else:
                    continue
    return df

df = rebase(df)

def drawdown_df_to_csv(df):
    for i in range(len(df.columns.values.tolist())-1):
        running_max = np.maximum.accumulate(df.iloc[:,i])
        running_max[running_max < 1] = 1
        df.iloc[:,i] = df.iloc[:,i] / running_max - 1
    return df.to_csv('drawdown.csv')

drawdown_df_to_csv(df)
