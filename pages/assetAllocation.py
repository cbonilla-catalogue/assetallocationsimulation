import dash
from dash.dependencies import Input, Output, State
import dash_design_kit as ddk
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np

from utils import makeAllocationSunbursts

from app import app, snap
from . import tasks

# https://plotly.com/python/treemaps/#treemap-of-a-rectangular-dataframe-with-continuous-color-argument-in-pxtreemap
# https://towardsdatascience.com/pandas-join-vs-merge-c365fd4fbf49
# https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
# https://plotly.com/python/treemaps/#treemap-of-a-rectangular-dataframe-with-continuous-color-argument-in-pxtreemap
# https://plotly.com/python/sunburst-charts/#basic-sunburst-plot-with-plotlyexpress

houseViewsDf = pd.read_csv(
    "./data/houseViews.csv", encoding="ISO-8859-1", engine="python"
)

stats = pd.read_csv("./data/descriptiveStats.csv", engine="python")

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
).set_index("Risk Asset Class")

correlationDf = pd.read_csv(
    "./data/correlationMatrixUpload.csv", engine="python"
).set_index("Index")

for i in correlationDf.columns:
    correlationDf[i] = assetAllocationDf.loc[i, "Standard Deviation"] * correlationDf[i]
    correlationDf.loc[i] = (
        assetAllocationDf.loc[i, "Standard Deviation"] * correlationDf.loc[i]
    )


def makeAllocationSunburst(data):
    dff = data
    dff["Proposed Allocation"] = dff["Proposed Allocation"].astype(float)

    tempDf = assetAllocationDf.reset_index().merge(
        dff, how="left", on=["Asset Class", "Sub Asset Class"]
    )
    mean = tempDf.fillna(0)["Arithmetic Mean"].to_numpy()
    allocation = tempDf.fillna(0)["Proposed Allocation"].to_numpy()
    portExpectedReturn = (mean * allocation).sum() / 100
    portStandardDeviation = (
        np.sqrt(
            np.asmatrix(allocation)
            * np.asmatrix(correlationDf.to_numpy())
            * np.asmatrix(allocation).T
        ).sum()
        / 100
    )

    allocatedPercentage = allocation.sum()
    card = (
        "Adjust allocations below: "
        + "{:.2f}%".format(allocatedPercentage)
        + " allocated"
    )
    figure = [
        # ddk.CardHeader(
        #    title='Proposed Asset Allocation',
        #    fullscreen=True,
        # ),
        ddk.CardHeader(
            title="Expected Return = " + "{:.2f}%".format(portExpectedReturn),
            fullscreen=False,
        ),
        ddk.CardHeader(
            title="Expected Portfolio Standard Deviation = "
            + "{:.2f}%".format(portStandardDeviation),
            fullscreen=False,
        ),
        ddk.Graph(
            id="scatter",
            figure=px.sunburst(
                dff,
                path=["Asset Class", "Sub Asset Class"],
                values="Proposed Allocation",
                color="Asset Class",
                color_discrete_map={
                    "Equity": "DFE0B9",
                    "Fixed Income": "505F9B",
                    "Cash & Cash Equivalent": "079BD3",
                    "Alternative Investments": "7B9B50",
                },
            ).update_traces(textinfo="label+percent root"),
        ),
    ]

    return figure, card, allocatedPercentage


def layout():
    return html.Div(
        [
            ddk.ControlCard(
                width=100,
                children=[
                    ddk.ControlItem(
                        dcc.Input(
                            id="financialAdvisor", placeholder="Type the advisors name"
                        ),
                        label="Financial Advisor",
                        width=25,
                    ),
                    ddk.ControlItem(
                        dcc.Input(id="clientName", placeholder="Type the client name"),
                        label="Client Name",
                        width=25,
                    ),
                    ddk.ControlItem(
                        dcc.Input(id="reportName", placeholder="Type a report name"),
                        label="Report Name",
                        width=25,
                    ),
                    ddk.ControlItem(
                        dcc.Dropdown(
                            id="businessType",
                            options=[
                                {"label": "Advisory", "value": "Advisory"},
                                {"label": "Brokerage", "value": "Brokerage"},
                            ],
                        ),
                        label="Client Account Type",
                        width=25,
                    ),
                    # ddk.ControlItem(
                    #    dcc.Dropdown(
                    #        id="modelSelection",
                    #        options=[
                    #            {
                    #                "label": "Conservative",
                    #                "value": "Conservative"
                    #            },
                    #            {
                    #                "label": "Conservative +",
                    #                "value": "Conservative Plus",
                    #            },
                    #            {
                    #                "label": "Moderate",
                    #                "value": "Moderate"
                    #            },
                    #            {
                    #                "label": "Aggressive",
                    #                "value": "Aggressive"
                    #            },
                    #        ],
                    #    ),
                    #    label="Client Risk Profile",
                    #    width=20,
                    # ),
                    html.Button("Run", id="run"),
                    html.Div(id="status"),
                ],
                orientation="horizontal",
            ),
            ddk.SectionTitle("Adjust your investment allocations"),
            ddk.Card(
                width=100,
                children=[
                    ddk.CardHeader(
                        title="Select a base risk allocation",
                        children=dcc.Dropdown(
                            id="riskModel",
                            options=[
                                {"label": "Conservative", "value": "Conservative"},
                                {
                                    "label": "Conservative Plus",
                                    "value": "Conservative Plus",
                                },
                                {"label": "Moderate", "value": "Moderate"},
                                {"label": "Aggressive", "value": "Aggressive"},
                                # {
                                #    "label": "Free Form",
                                #    "value": "Free Form"
                                # },
                            ],
                            value="Moderate",
                        ),
                        # fullscreen=True,
                    ),
                    # ddk.Row([
                    # ddk.Card(
                    #    width=50,children = ddk.Graph(id="summary")),
                    ddk.Card(
                        width=50,
                        children=[
                            ddk.CardHeader(
                                id="percentAllocated",
                                # title='Input your proposed allocations',
                                fullscreen=False,
                            ),
                            # ddk.SectionTitle("Input your proposed allocations"),
                            ddk.DataTable(
                                id="dataTableAllocation",
                                columns=[
                                    {
                                        "name": "Asset Class",
                                        "id": "Asset Class",
                                        "editable": False,
                                    },
                                    {
                                        "name": "Sub Asset Class",
                                        "id": "Sub Asset Class",
                                        "editable": False,
                                    },
                                    {
                                        "name": "Proposed Allocation",
                                        "id": "Proposed Allocation",
                                        "editable": True,
                                    },
                                ],
                                # style_table={
                                #    'maxHeight': '500px',
                                #    'overflowY': 'scroll'
                                # },
                                # filter_action='False'
                                style_as_list_view=True,
                                style_cell={
                                    "height": "auto",
                                    # all three widths are needed
                                    "minWidth": "10px",
                                    "width": "160px",
                                    "maxWidth": "160px",
                                    "whiteSpace": "normal",
                                    "textAlign": "left",
                                },
                            ),
                        ],
                    ),
                    ddk.Card(width=50, id="yourAllocation"),
                ],
            ),
            dcc.Store(id="intermediate-value"),
            dcc.Store(id="allocatedCheck"),
        ]
    )

@app.callback(
    Output("yourAllocation", "children"),
    Output("percentAllocated", "title"),
    Output("allocatedCheck", "value"),
    Input("dataTableAllocation", "data"),
    Input("dataTableAllocation", "columns"),
)
def update_graph(rows, columns):
    dff = pd.DataFrame(rows, columns=[c["name"] for c in columns])
    dff["Risk Objective"] = "Proposed Allocation"

    fig = makeAllocationSunburst(data=dff)
    allocatedPercentage = fig[2]
    card = fig[1]
    fig = fig[0]

    return fig, card, allocatedPercentage


@app.callback(Output("intermediate-value", "data"), Input("riskModel", "value"))
def clean_data(value):
    # some expensive clean data step
    securitySelection = tacticalAllocationDf.loc[
        tacticalAllocationDf["Risk Objective"] == value
    ]
    # securitySelection = securitySelection.merge(stats, left_on=['Asset Class','Sub Asset Class'], right_on=['Asset Class','Sub Asset Class'])
    # dff = tacticalAllocationDf.loc[tacticalAllocationDf['Risk Objective']==value]
    # count = securitySelection.groupby(['Asset Class','Sub Asset Class']).count()['Allocation'].reset_index()
    # securitySelection = securitySelection.merge(count, left_on=['Asset Class','Sub Asset Class'], right_on=['Asset Class','Sub Asset Class'])
    # securitySelection['Proposed Allocation'] = securitySelection['Allocation_x']/securitySelection['Allocation_y']
    # securitySelection = securitySelection[['Fund Name', 'ISIN','Asset Class', 'Sub Asset Class', 'Proposed Allocation']]

    # more generally, this line would be
    # json.dumps(cleaned_df)
    return securitySelection.to_json(date_format="iso", orient="split")


@app.callback([Output("dataTableAllocation", "data")], [Input("riskModel", "value")])
def updateTable(value):
    securitySelection = tacticalAllocationDf.loc[
        tacticalAllocationDf["Risk Objective"] == value
    ]
    # securitySelection = securitySelection.merge(stats, left_on=['Asset Class','Sub Asset Class'], right_on=['Asset Class','Sub Asset Class'])

    # count = securitySelection.groupby(['Asset Class','Sub Asset Class']).count()['Allocation'].reset_index()
    # securitySelection = securitySelection.merge(count, left_on=['Asset Class','Sub Asset Class'], right_on=['Asset Class','Sub Asset Class'])
    securitySelection["Proposed Allocation"] = securitySelection["Allocation"]
    securitySelection = securitySelection[
        ["Asset Class", "Sub Asset Class", "Proposed Allocation"]
    ]

    tempDf = assetAllocationDf.reset_index().merge(
        securitySelection, how="left", on=["Asset Class", "Sub Asset Class"]
    )
    mean = tempDf.fillna(0)["Arithmetic Mean"].to_numpy()
    allocation = tempDf.fillna(0)["Proposed Allocation"].to_numpy()
    portExpectedReturn = (mean * allocation).sum()
    portStandardDeviation = np.sqrt(
        np.asmatrix(allocation)
        * np.asmatrix(correlationDf.to_numpy())
        * np.asmatrix(allocation).T
    ).sum()

    # securitySelection.to_csv('out.csv')

    return [securitySelection.to_dict("records")]


@app.callback(
    Output("status", "children"),
    [Input("run", "n_clicks"),
    Input('allocatedCheck','value')],
    [
        State("dataTableAllocation", "derived_virtual_data"),
        State("financialAdvisor", "value"),
        State("clientName", "value"),
        State("reportName", "value"),
        # State("modelSelection", "value"),
        State("businessType", "value"),
    ],
    prevent_initial_call=True,
)
def update_status(
    n_clicks,
    allocatedCheck,
    rows,
    financialAdvisor,
    clientName,
    reportName,
    # modelSelection,
    businessType,
):
    # Submit the long-running task to the task queue
    if n_clicks == None:
        text = []
    elif financialAdvisor is None or clientName is None or reportName is None:
        text = html.Div(str('   Input data seems to be missing, please review.').upper(),style={"fontSize": "14px",'font-weight':'bold'})
    elif allocatedCheck != 100:
        text = (
            html.Div(
                str(
                    """ ERROR: MAKE SURE YOUR ALLOCATION SUMS TO 100%
                    ONCE YOU UPDATE THE ALLOCATION TO 100% THE REPORT WILL IMMEDIATELY RUN"""
                ),style={"fontSize": "14px",'font-weight':'bold'},
            ),
        )
    elif allocatedCheck == 100:
        snapshot_id = snap.snapshot_save_async(
            tasks.run_model,
            rows=rows,
            financialAdvisor=financialAdvisor,
            clientName=clientName,
            reportName=reportName,
            # modelSelection=modelSelection,
            businessType=businessType,
        )
        # Save the model parameters so that they can be loaded later
        snap.meta_update(
            snapshot_id,
            dict(
                rows=rows,
                financialAdvisor=financialAdvisor,
                clientName=clientName,
                reportName=reportName,
                # modelSelection=modelSelection,
                businessType=businessType,
            ),
        )
        text = html.Div(
            [
                "Running! This takes about 5 minutes to complete. ",
                dcc.Link(
                    "View results in the archive tab",
                    href=app.get_relative_path("/archive"),
                ),
            ]
        )
    # Update 5 to be however long you think this will take :)
    return text
