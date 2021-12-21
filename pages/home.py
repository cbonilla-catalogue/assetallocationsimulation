from dash.dependencies import Input, Output
import dash_design_kit as ddk
from dash import html, dcc
from app import app
import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd

tacticalAllocationDf = pd.read_csv(
    "./data/tacticalAllocation.csv", encoding="ISO-8859-1", engine="python"
)[["Risk Objective", "Asset Class", "Sub Asset Class", "Allocation"]]

tacticalAllocationDf = tacticalAllocationDf[
    ["Risk Objective", "Asset Class", "Sub Asset Class", "Allocation"]
]

strategicAllocationDf = pd.read_csv(
    "./data/strategicAllocations.csv", encoding="ISO-8859-1", engine="python"
)

assetAllocationDf = pd.read_csv(
    "./data/assetAllocationUpload.csv", engine="python"
).set_index('Risk Asset Class')

correlationDf = pd.read_csv(
    "./data/correlationMatrixUpload.csv", engine="python"
).set_index('Index')

for i in correlationDf.columns:
    correlationDf[i]=assetAllocationDf.loc[i,'Standard Deviation']*correlationDf[i]
    correlationDf.loc[i]=assetAllocationDf.loc[i,'Standard Deviation']*correlationDf.loc[i]


def makeAllocationSunbursts(riskObjective):
    dff = tacticalAllocationDf[tacticalAllocationDf["Risk Objective"] == riskObjective]
    dff["Risk Objective"] = dff["Risk Objective"] + " Allocation"

    tempDf = assetAllocationDf.reset_index().merge(dff, how='left', on=['Asset Class','Sub Asset Class'])
    mean = tempDf.fillna(0)['Arithmetic Mean'].to_numpy()
    allocation = tempDf.fillna(0)['Allocation'].to_numpy()
    portExpectedReturn = (mean * allocation).sum()/100
    portStandardDeviation = np.sqrt(np.asmatrix(allocation) * np.asmatrix(correlationDf.to_numpy()) * np.asmatrix(allocation).T).sum()/100

    return ddk.Card(
        width=50,
        children=[
            ddk.CardHeader(
                title=riskObjective + " Model Allocation",
                fullscreen=True,
            ),
            ddk.CardHeader(
                title='Expected Return = '+"{:.2f}%".format(portExpectedReturn),
                fullscreen=False,
            ),
            ddk.CardHeader(
                title="Expected Portfolio Standard Deviation = "+"{:.2f}%".format(portStandardDeviation),
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
#                ddk.DataTable(
#       id='table',
#      columns=[{"name": i, "id": i} for i in dff[['Sub Asset Class','Allocation']]],
#       data=dff.to_dict("rows"),
#       editable=False
#   ),
        ],
    )


def layout():
    return html.Div(
        [
            html.Iframe(
                src="https://player.vimeo.com/video/528579544",
                style={"height": "567px", "width": "100%"},
            ),
            ddk.Block(
                width=100,
                children=[
                    makeAllocationSunbursts(riskObjective="Conservative"),
                    makeAllocationSunbursts(riskObjective="Conservative Plus"),
                    makeAllocationSunbursts(riskObjective="Moderate"),
                    makeAllocationSunbursts(riskObjective="Aggressive"),
                ],
            ),
        ]
    )
