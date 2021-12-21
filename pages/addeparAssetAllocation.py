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

import requests
import io
from datetime import date
import dash_enterprise_auth

# https://plotly.com/python/treemaps/#treemap-of-a-rectangular-dataframe-with-continuous-color-argument-in-pxtreemap
# https://towardsdatascience.com/pandas-join-vs-merge-c365fd4fbf49
# https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
# https://plotly.com/python/treemaps/#treemap-of-a-rectangular-dataframe-with-continuous-color-argument-in-pxtreemap
# https://plotly.com/python/sunburst-charts/#basic-sunburst-plot-with-plotlyexpress

addeparPortfolios = pd.read_csv(
    "./data/addeparAdvisorsPortfolios.csv", encoding="ISO-8859-1", engine="python"
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
    dff["Value (USD)"] = dff["Value (USD)"].astype(float)

    tempDf = assetAllocationDf.reset_index().merge(
        dff, how="left", on=["Asset Class", "Sub Asset Class"]
    )
    mean = tempDf.fillna(0)["Arithmetic Mean"].to_numpy()
    allocation = tempDf.fillna(0)["Value (USD)"].to_numpy()
    portExpectedReturn = (mean * allocation).sum() / 100000
    # portStandardDeviation = np.sqrt(np.asmatrix(allocation) * np.asmatrix(correlationDf.to_numpy()) * np.asmatrix(allocation).T).sum()/100

    card = (
        "Adjust allocations below: " + "{:.2f}%".format(allocation.sum()) + " allocated"
    )
    figure = [
         ddk.CardHeader(
            title="Expected Return = "+"{:.2f}%".format(portExpectedReturn),
            fullscreen=False,
         ),
        # ddk.CardHeader(
        #    title="Expected Portfolio Standard Deviation = "+"{:.2f}%".format(portStandardDeviation),
        #    fullscreen=False,
        # ),
        ddk.Graph(
            id="scatter",
            figure=px.sunburst(
                dff,
                path=["Asset Class", "Sub Asset Class"],
                values="Value (USD)",
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

    return figure, card


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
                        width=20,
                    ),
                    ddk.ControlItem(
                        dcc.Input(id="clientName", placeholder="Type the client name"),
                        label="Client Name",
                        width=20,
                    ),
                    ddk.ControlItem(
                        dcc.Input(id="reportName", placeholder="Type a report name"),
                        label="Report Name",
                        width=20,
                    ),
                    #ddk.ControlItem(
                    #    dcc.Dropdown(
                    #        id="businessTypeNew",
                    #        options=[
                    #            {"label": "Advisory", "value": "Advisory"},
                    #            {"label": "Brokerage", "value": "Brokerage"},
                    #        ],
                    #    ),
                    #    label="Client Account Type",
                    #    width=20,
                    #),
                    ddk.ControlItem(
                        dcc.Dropdown(
                            id="modelSelectionNew",
                            options=[
                                {"label": "Conservative", "value": "Conservative"},
                                {
                                    "label": "Conservative +",
                                    "value": "Conservative Plus",
                                },
                                {"label": "Moderate", "value": "Moderate"},
                                {"label": "Aggressive", "value": "Aggressive"},
                            ],
                        ),
                        label="Client Risk Profile",
                        width=20,
                    ),
                    html.Button("Run", id="runNew"),
                    html.Div(id="statusAddepar"),
                ],
                orientation="horizontal",
            ),
            ddk.SectionTitle("Adjust your investment allocations"),
            ddk.Card(
                width=100,
                children=[
                    ddk.CardHeader(
                        title="Select an portfolio type",
                        children=dcc.Dropdown(
                            id="portfolioTypeDropdown",
                            options=[
                                {"label": "Client", "value": "Entity"},
                                {"label": "Account", "value": "Account"},
                            ],
                            value="Entity",
                        ),
                        # fullscreen=True,
                    ),
                    ddk.CardHeader(
                        title="Select an account number",
                        children=dcc.Dropdown(
                            id="accountNumberDropdown",
                            #options=[{"label": i, "value": i} for i in addeparPortfolios["Holding Account Number"].dropna()]
                        ),
                        # fullscreen=True,
                    ),
                    # ddk.Row([
                    # ddk.Card(
                    #    width=50,children = ddk.Graph(id="summary")),
                    ddk.Card(
                        width=50,
                        children=[
                            # ddk.SectionTitle("Input your Value (USD)s"),
                            ddk.DataTable(
                                id="AddeparDataTableAllocation",
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
                                        "name": "Security",
                                        "id": "Security",
                                        "editable": False,
                                    },
                                    {
                                        "name": "Value (USD)",
                                        "id": "Value (USD)",
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
                            )
                        ],
                    ),
                    ddk.Card(width=50, id="Addeparallocation"),
                ],
            ),
        ]
    )


@app.callback(
    [Output("accountNumberDropdown", "options")],
    [Input("portfolioTypeDropdown", "value")],
)
def display_output(value):
    username = dash_enterprise_auth.get_username()
    if value == 'Account':
        value = addeparPortfolios.loc[addeparPortfolios["webappUserId"] == username]
        accountList = [list({"label": i, "value": i} for i in value["Holding Account Number"])]
    elif value == 'Client':
        value = addeparPortfolios
        accountList = [list({"label": i, "value": i} for i in value["Holding Account Number"])]
    return accountList

@app.callback(
    [Output("AddeparDataTableAllocation", "data")],
    [Input("accountNumberDropdown", "value")],
)
def updateTable(value):

    value = addeparPortfolios.loc[addeparPortfolios["Holding Account Number"] == value][
        "Entity ID"
    ]  # .dropna(subset=['Holding Account Number'])

    url = "https://insigneo.addepar.com/api/v1/portfolio/views/287490/results"
    querystring = {
        "portfolio_type": "ENTITY",
        "portfolio_id": value,
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "output_type": "CSV",
    }

    headers = {
        "Accept": "application/vnd.api+json",
        "Addepar-Firm": "286",
        "Authorization": "Basic MmYyNDEyMmItNjhmOS00ZjgzLWEwMTgtMGJlYzI3OWFhM2QwOmJhY0ZXb2NzSzJpS3ZGTXYzNjF2MGhpMWpGdUNTa1pnTUl6eXhSSFQ=",
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    urlData = response.content
    rawData = pd.read_csv(io.StringIO(urlData.decode("utf-8")))
    rawData = rawData.loc[rawData["Value (USD)"] != 0]

    return [rawData.to_dict("records")]


@app.callback(
    Output("Addeparallocation", "children"),
    Output("Addeparallocation", "title"),
    Input("AddeparDataTableAllocation", "data"),
    Input("AddeparDataTableAllocation", "columns"),
)
def update_graph(rows, columns):
    dff = pd.DataFrame(rows, columns=[c["name"] for c in columns])

    fig = makeAllocationSunburst(data=dff)
    card = fig[1]
    fig = fig[0]

    return fig, card

@app.callback(
    Output("statusAddepar", "children"),
    [Input("runNew", "n_clicks")],
    [
        State("AddeparDataTableAllocation", "derived_virtual_data"),
        State("financialAdvisor", "value"),
        State("clientName", "value"),
        State("reportName", "value"),
        State("modelSelectionNew", "value"),
    ],
    prevent_initial_call=True,
)
def update_status(
    n_clicks,
    rows,
    financialAdvisor,
    clientName,
    reportName,
    modelSelection,
):
    # Submit the long-running task to the task queue
    snapshot_id = snap.snapshot_save_async(
        tasks.run_model,
        rows=rows,
        financialAdvisor=financialAdvisor,
        clientName=clientName,
        reportName=reportName,
        modelSelection=modelSelection,
        businessType='Advisory',
    )
    # Save the model parameters so that they can be loaded later
    snap.meta_update(
        snapshot_id,
        dict(rows=rows,
             financialAdvisor=financialAdvisor,
             clientName=clientName,
             reportName=reportName,
             modelSelection=modelSelection,
             businessType='Advisory'),
    )
    # Update 5 to be however long you think this will take :)
    return html.Div([
        "Running! This takes about 5 minutes to complete. ",
        dcc.Link(
            "Wait for the results in the archive",
            href=app.get_relative_path("/archive"),
        ),
    ])