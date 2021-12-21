from dash.dependencies import Input, Output
import dash_design_kit as ddk
from dash import html, dcc
from app import app
import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd

def makeAllocationSunbursts(riskObjective):
    dff = tacticalAllocationDf[tacticalAllocationDf["Risk Objective"] == riskObjective]
    dff["Risk Objective"] = dff["Risk Objective"] + " Allocation"

    tempDf = assetAllocationDf.reset_index().merge(dff, how='left', on=['Asset Class','Sub Asset Class'])
    mean = tempDf.fillna(0)['Arithmetic Mean'].to_numpy()
    allocation = tempDf.fillna(0)['Allocation'].to_numpy()
    portExpectedReturn = (mean * allocation).sum()
    portStandardDeviation = np.sqrt(np.asmatrix(allocation) * np.asmatrix(correlationDf.to_numpy()) * np.asmatrix(allocation).T).sum()

    return ddk.Card(
        width=50,
        children=[
            ddk.CardHeader(
                title=riskObjective + " Model Allocation",
                fullscreen=True,
            ),
            ddk.CardHeader(
                title="Expected Return = "+str(portExpectedReturn),
                fullscreen=False,
            ),
            ddk.CardHeader(
                title="Expected Portfolio Standard Deviation = "+str(portStandardDeviation),
                fullscreen=False,
            ),
            ddk.Graph(
                id="scatter",
                figure=px.sunburst(
                    dff,
                    path=["Asset Class", "Sub Asset Class"],
                    values="Allocation",
                    color='Asset Class',
                    color_discrete_map={'Equity':'DFE0B9', 'Fixed Income':'505F9B', 'Cash & Cash Equivalent':'079BD3',
                    'Alternative Investments':'7B9B50'},
                ).update_traces(textinfo="label+percent root"),
            ),
                ddk.DataTable(
       id='table',
       columns=[{"name": i, "id": i} for i in dff[['Sub Asset Class','Allocation']]],
       data=dff.to_dict("rows"),
       editable=False
   ),
        ],
    )