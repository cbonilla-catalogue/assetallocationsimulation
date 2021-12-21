import dash_design_kit as ddk
#from dash_table import FormatTemplate
from dash.dash_table import FormatTemplate
from dash import html, dash_table
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Symbol

import plotly.figure_factory as ff


from app import app, snap
from datetime import datetime
import math

# from portHoldings import PortfolioHoldingsTable

from disclaimers import addDisclaimers
from datatableHeatmap import discrete_background_color_bins

houseViewsDf = pd.read_csv(
    "./data/houseViews.csv", encoding="ISO-8859-1", engine="python"
)

historicalReturnsDf = pd.read_csv("./data/historicalReturns.csv")

historicalReturnsDf["Date"] = pd.to_datetime(historicalReturnsDf["Date"])
historicalReturnsDf = historicalReturnsDf.set_index("Date")

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

correlationPlotDf = pd.read_csv(
    "./data/correlationMatrixUpload.csv", engine="python"
).set_index("Index")

assetAllocationPerformance = pd.read_csv(
    "./data/assetAllocationWinnersLosers.csv", engine="python"
).set_index("Risk Asset Class")

tidyAssetAllocationPerformanceDf = pd.read_csv(
    "./data/tidyAssetAllocationWinnersLosers.csv", engine="python"
)

model_df = pd.read_csv(
    "./data/modelPortfolios.csv", encoding="ISO-8859-1", engine="python"
)

footer = ddk.PageFooter(
    "INSIGNEO, LLC This is not a formal presentation nor account statement of your account and its performance results Please refer to your official statement for accurate information."
)


def makeAllocationSunbursts(proposedAllocationDf):
    dff = proposedAllocationDf

    tempDf = assetAllocationDf.reset_index().merge(
        dff, how="left", on=["Asset Class", "Sub Asset Class"]
    )
    allocation = tempDf.fillna(0)["Proposed Allocation"].to_numpy()

    return ddk.Graph(
        id="scatter",
        figure=px.sunburst(
            dff,
            path=["Asset Class", "Sub Asset Class"],
            values="Proposed Allocation",
            color="Asset Class",
            color_discrete_map={
                "Equity": "#DFE0B9",
                "Fixed Income": "#505F9B",
                "Cash & Cash Equivalent": "#079BD3",
                "Alternative Investments": "#7B9B50",
            },
        )
        .update_traces(opacity=0.5, selector=dict(type='sunburst'),textinfo="label+percent root")
        .update_layout(
            {
                "paper_bgcolor": "var(--report_background_page)",
                "plot_bgcolor": "var(--report_background_page)",
            },
            legend=dict(
                # yanchor="middle",
                y=-0.3,
                # xanchor="left",
                x=0.1,
            ),
        ),
    )


def make_header(text):
    return ddk.Row(
        style={"height": "8%"},
        children=[
            ddk.Block(
                width=85,
                children=html.H2("{}".format(text).upper()),
            ),
            ddk.Block(
                width=15,
                children=html.Img(
                    src=app.get_asset_url("logo.png"),
                    style={"height": "90%"},
                ),
            ),
        ],
    )


money = FormatTemplate.money(0)
percentage = FormatTemplate.percentage(2)
columns_table_one = [
    dict(id="Asset Class", name="Asset Class"),
    dict(id="Sub Asset Class", name="Sub Asset Class"),
    dict(
        id="Proposed Allocation",
        name="Proposed Allocation",
        type="numeric",
        format=percentage,
    ),
]

columns_table_two = [
    dict(id="Asset Class", name="Asset Class"),
    dict(id="Sub Asset Class", name="Sub Asset Class"),
    dict(id="Risk Asset Class", name="Risk Asset Class"),
    dict(id="Proxy Index", name="Proxy Index"),
    dict(
        id="Model Yearly Expected Return",
        name="Model Yearly Expected Return",
        type="numeric",
        format=percentage,
    ),
    dict(
        id="Model Yearly Standard Deviation",
        name="Model Yearly Standard Deviation",
        type="numeric",
        format=percentage,
    ),
    dict(
        id="Proposed Allocation",
        name="Proposed Allocation",
        type="numeric",
        format=percentage,
    ),
]

columns_table_three = [
    dict(id="Asset Class", name="Asset Class"),
    dict(id="Sub Asset Class", name="Sub Asset Class"),
    dict(id="Risk Asset Class", name="Risk Asset Class"),
    dict(id="Proxy Index", name="Proxy Index"),
    dict(
        id="Proposed Allocation",
        name="Proposed Allocation",
        type="numeric",
        format=percentage,
    ),
]

columnsHistoricalAnnualized = [
    dict(id="index", name="Risk Asset Class"),
    dict(
        id="1 year",
        name="1 year",
        type="numeric",
        format=percentage,
    ),
    dict(
        id="3 year",
        name="3 year",
        type="numeric",
        format=percentage,
    ),
    dict(
        id="5 year",
        name="5 year",
        type="numeric",
        format=percentage,
    ),
]

def make_page(data, i, j, columns, clientName):
    """
    Generate a page containing a subset of the tabular data
    @param data: The data subset formatted as records
    @param i: The current page
    @param j: The total number of data pages
    """
    return ddk.Page(
        [
            ddk.Row(
                style={"height": "8%"},
                children=[
                    ddk.Block(
                        width=85,
                        children=html.H2("Portfolio SECURITY SELECTION".upper()),
                    ),
                    ddk.Block(
                        width=15,
                        children=html.Img(
                            src=app.get_asset_url("logo.png"),
                            style={"height": "90%"},
                        ),
                    ),
                ],
            ),
            ddk.Block(
                width=95,
                margin=5,
                children=ddk.DataTable(
                    columns=columns,
                    style_cell_conditional=[
                        {"if": {"column_id": "Security"}, "width": "325px"},
                        {
                            "if": {"column_id": "Weight"},
                            "textAlign": "right",
                        },
                        {
                            "if": {"column_id": "Investment Amount"},
                            "textAlign": "right",
                        },
                        {"if": {"column_id": "Asset Class"}, "fontWeight": "bold"},
                    ],
                    style_cell={
                        "whiteSpace": "normal",
                        "height": "auto",
                        "textOverflow": "ellipsis",
                        "textAlign": "left",
                    },
                    data=data,
                    fill_width=True,
                    style_as_list_view=True,
                    style_header={"backgroundColor": "white", "fontWeight": "bold"},
                ),
            ),
            footer,
        ]
    )


def layout(snapshot_id):
    # This function is called when the snapshot URL is loaded by an end
    # user (displaying the web report) or by the Snapshot Engine's
    # PDF rendering service (when taking a PDF snapshot)
    #
    # The data that was saved by the asynchronous task is loaded and
    # then transformed into a set of `ddk.Report` calls.
    # We're using mock data here just for illustration purposes.
    #
    # You can also save the `ddk.Report` in the task queue instead
    # of just the dataset. Then, you would simply `return snapshot`
    # here. If you saved report, you wouldn't be able to change
    # the layout of the report after it was saved. In this case model,
    # you can update the look and feel of your report in this function
    # _on-the-fly_ when the snapshot is loaded. Note that any changes
    # that you make here won't be reflected in the previously saved PDF
    # version

    snapshot = snap.snapshot_get(snapshot_id)
    df3 = pd.DataFrame(snapshot["uploadedData"])
    df3['Proposed Allocation'] = df3['Proposed Allocation'].astype(float)/100
    df3 = df3.loc[(df3['Proposed Allocation']!=0)]
    financialAdvisor = snapshot["financialAdvisor"]
    clientName = snapshot["clientName"]
    reportName = snapshot["reportName"]
    #modelSelection = snapshot["modelSelection"]
    businessType = snapshot["businessType"]
    createdTime = snap.meta_get(snapshot_id, key="created_time")

    return report(
        df3,
        financialAdvisor,
        clientName,
        reportName,
        #modelSelection,
        createdTime,
        businessType,
    )


def report(
    df3=None,
    financialAdvisor=None,
    clientName=None,
    reportName=None,
    #modelSelection=None,
    createdTime=None,
    businessType=None,
):
    # Generate the report a separate function from the snapshot layout
    # so that you can debug the report under a separate URL

    # Check if we're in dev mode, where the report is generated under the
    # /dev URL just to tweak the report layout

    df3 = assetAllocationDf.reset_index().merge(
        df3, how="left", on=["Asset Class", "Sub Asset Class"]
    )
    df3["Proposed Allocation"] = df3["Proposed Allocation"].astype(float)
    mean = df3.fillna(0)["Arithmetic Mean"].to_numpy()
    allocation = df3.fillna(0)["Proposed Allocation"].to_numpy()
    portExpectedReturn = (mean * allocation).sum()

    portStandardDeviation = np.sqrt(
        np.asmatrix(allocation)
        * np.asmatrix(correlationDf.to_numpy())
        * np.asmatrix(allocation).T
    ).sum()

    # historicalReturnsDf = historicalReturnsDf[df3.dropna()['Risk Asset Class']]
    temp = []
    for i in historicalReturnsDf[df3.dropna()["Risk Asset Class"]].columns:
        temp.append(
            historicalReturnsDf[df3.dropna()["Risk Asset Class"]][
                i
            ].first_valid_index()
        )
    commonStartDate = max(temp)
    endDate = max(historicalReturnsDf.index)

    summaryStatsDF = df3.dropna()
    summaryStatsDF = summaryStatsDF[
        [
            "Asset Class",
            "Sub Asset Class",
            "Risk Asset Class",
            "Proxy Index",
            "Arithmetic Mean",
            "Standard Deviation",
            "Proposed Allocation",
        ]
    ].rename(
        columns={
            "Arithmetic Mean": "Model Yearly Expected Return",
            "Standard Deviation": "Model Yearly Standard Deviation",
        }
    )
    summaryStatsDF["Model Yearly Expected Return"] = (
        summaryStatsDF["Model Yearly Expected Return"] / 100
    )
    summaryStatsDF["Model Yearly Standard Deviation"] = (
        summaryStatsDF["Model Yearly Standard Deviation"] / 100
    )

    statsTemp = {'Asset Class':['Proposed Portfolio'],'Sub Asset Class':['Proposed Portfolio'],'Risk Asset Class':['Proposed Portfolio'],
    'Proxy Index': ['N/A'], 'Model Yearly Expected Return': [portExpectedReturn/100],'Model Yearly Standard Deviation': [portStandardDeviation/100],'Proposed Allocation': 1}
    statsTemp = pd.DataFrame(data=statsTemp)
    summaryStatsDF = summaryStatsDF.append(statsTemp, ignore_index=True)

    historical = historicalReturnsDf[df3.dropna()["Risk Asset Class"]]
    historical = (
        historical.reset_index()
        .loc[historical.reset_index()["Date"] >= commonStartDate]
        .set_index("Date")
    )

    calculatedReturnDf = pd.DataFrame()
    tempLength = len(historical["Equity - US Large Cap"])
    fiveYear = historical.iloc[tempLength - 60 : tempLength] / 100
    threeYear = historical.iloc[tempLength - 36 : tempLength] / 100
    oneYear = historical.iloc[tempLength - 12 : tempLength] / 100

    #calculatedReturnDf["1 year"] = oneYear.add(1).prod() ** (12 / 60) - 1
    #calculatedReturnDf["3 year"] = threeYear.add(1).prod() ** (12 / 60) - 1
    #calculatedReturnDf["5 year"] = fiveYear.add(1).prod() ** (12 / 60) - 1

    historicalCumulativeReturnsDf = pd.DataFrame()
    for i in historical.columns:
        historicalCumulativeReturnsDf[i] = 100 * np.exp((
            historical.loc[:, i] / 100
        ).cumsum())
    
    for i in historical.columns:
        historical[i] = (
            historical[i]
            * df3.loc[df3["Risk Asset Class"] == i][
                "Proposed Allocation"
            ].tolist()[0]
        )

    historicalProposed = (historical / 100).sum(axis=1)
    fiveYear['Proposed Portfolio'] = historicalProposed.iloc[tempLength - 60 : tempLength]
    threeYear['Proposed Portfolio'] = historicalProposed.iloc[tempLength - 36 : tempLength]
    oneYear['Proposed Portfolio'] = historicalProposed.iloc[tempLength - 12 : tempLength]

    calculatedReturnDf["1 year"] = oneYear.add(1).prod() ** (12 / 60) - 1
    calculatedReturnDf["3 year"] = threeYear.add(1).prod() ** (12 / 60) - 1
    calculatedReturnDf["5 year"] = fiveYear.add(1).prod() ** (12 / 60) - 1

    portReturnIndex = 100 * np.exp((historical / 100).sum(axis=1).cumsum())
    portReturnIndexChart = portReturnIndex.reset_index().rename(columns={0: "Historical Performance"})
    
    #portReturnIndex = (1 + ((historical / 100).sum(axis=1))).cumprod() - 1
    #portReturnIndexChart = (
    #    ((portReturnIndex + 1) * 100)
    #    .reset_index()
    #    .rename(columns={0: "Historical Performance"})
    #)

    historicalCumulativeReturnsDf["Proposed Allocation"] = portReturnIndex

    proposalHistoricalMean = (((historical / 100).sum(axis=1).mean() + 1)**12)-1
    proposalHistoricalStandardDeviation = (historical / 100).sum(axis=1).std()#*math.sqrt(12)#*math.sqrt(4)
    #proposalHistoricalStandardDeviation = (historical / 100).sum(axis=1).std()*math.sqrt(len((historical / 100).sum(axis=1)))

    tidyhistoricalCumulativeReturnsDf = pd.melt(
        historicalCumulativeReturnsDf.reset_index(),
        id_vars=["Date"],
        value_vars=historicalCumulativeReturnsDf.columns.tolist(),
        var_name="Investments",
        value_name="Historical Return",
    )

    sunburstFig = makeAllocationSunbursts(df3)

    heatmapDf = tidyAssetAllocationPerformanceDf[
        tidyAssetAllocationPerformanceDf["Risk Asset Class"].isin(
            historical.columns
        )
    ]
    heatmapDf = heatmapDf.loc[heatmapDf["Risk Asset Class"] != "Cash"]
    heatmapDfPivot = df3.dropna()["Risk Asset Class"]
    heatmapDfPivot = heatmapDfPivot.reset_index().merge(
        assetAllocationPerformance, how="left", on=["Risk Asset Class"]
    ).drop(columns=['Proxy Index','SecId','index'])

    #heatmapDfPivot = assetAllocationPerformance.drop(columns=['Proxy Index','SecId'])#.isin(df3.dropna()["Risk Asset Class"])
    #print(df3.dropna()["Risk Asset Class"])

    historicalAssetAllocationStats = tidyAssetAllocationPerformanceDf.pivot(index='Year', columns='Risk Asset Class', values='Yearly Return (%)')[df3.dropna()["Risk Asset Class"]]

    historicalAssetAllocationStatsChart = pd.DataFrame(data=historicalAssetAllocationStats.mean()).rename(columns={0: 'Historical Yearly Mean Return'})
    portStatsTemp = historicalAssetAllocationStatsChart.reset_index().merge(
        df3, how="left", on=["Risk Asset Class"])
    portStatsTemp['Portfolio Historical Yearly Mean Return'] = portStatsTemp['Historical Yearly Mean Return']*portStatsTemp['Proposed Allocation']
    portStatsTemp['Portfolio Historical Standard Deviation'] = portStatsTemp['Standard Deviation']*portStatsTemp['Proposed Allocation']
    historicalAssetAllocationTemp = pd.DataFrame(data=historicalAssetAllocationStats.std()).rename(columns={0: 'Historical Yearly Standard Deviation'})
    statsTemp = {'Risk Asset Class':['Proposed Portfolio'],'Historical Yearly Mean Return': [portStatsTemp['Portfolio Historical Yearly Mean Return'].sum()], 'Historical Yearly Standard Deviation': [portStatsTemp['Portfolio Historical Standard Deviation'].sum()],'Proposed Allocation': 1,'Asset Class':'Portfolio'}
    statsTemp = pd.DataFrame(data=statsTemp)
    historicalAssetAllocationStatsChart = historicalAssetAllocationStatsChart.join(historicalAssetAllocationTemp).reset_index()
    historicalAssetAllocationStatsChart = historicalAssetAllocationStatsChart.reset_index().merge(
        df3[['Risk Asset Class','Asset Class','Proposed Allocation']], how="left", on=["Risk Asset Class"])

    historicalAssetAllocationStatsChart = historicalAssetAllocationStatsChart.append(statsTemp, ignore_index=True)
    
    (historicalStyles, historicalLegend) = discrete_background_color_bins(heatmapDfPivot)
    
    historicalBoxPlot = px.box(
        data_frame = heatmapDf,
        y="Yearly Return (%)",
        x="Risk Asset Class",
        title="Yearly Historical Return Distributions",
    )

    num_simulations = 5000
    portMonteCarlo = np.random.default_rng().normal(
        portExpectedReturn, portStandardDeviation, num_simulations
    )
    portMonteCarlo = pd.DataFrame(
        portMonteCarlo, columns=["Proposal Simulated Return Distribution"]
    )
    
    portMonteCarloTimeseries = pd.DataFrame()

    for i in range(0,30):
        portMonteCarloTime = np.random.default_rng().normal(
        portExpectedReturn, portStandardDeviation, 10)
        portMonteCarloTime = np.where(portMonteCarloTime > (portExpectedReturn+(1.25*portStandardDeviation)), portExpectedReturn, portMonteCarloTime)
        portMonteCarloTimeseries[("Simulated Return v"+str(i))] = np.insert(100000 * np.exp((portMonteCarloTime / 100).cumsum()),0, 100000)

    #portMonteCarloTimeseries[("Simulated Return v"+str(31))] = 100000 * np.exp((np.random.default_rng().normal(
    #    (portExpectedReturn-(1*portStandardDeviation)), portStandardDeviation, 20) / 100).cumsum())
       
    tidySimulationReturnIndex = pd.melt(
        portMonteCarloTimeseries.reset_index(),
        id_vars=["index"],
        value_vars=portMonteCarloTimeseries.columns.tolist(),
        var_name="Investments",
        value_name="Simulated Investment Growth",
    ).rename(columns={"index": "Simulated Year"})

    portfolioValueMin, portfolioValueMax = (
        tidySimulationReturnIndex[tidySimulationReturnIndex["Simulated Year"] == 10][
            "Simulated Investment Growth"
        ].min(),
        tidySimulationReturnIndex[tidySimulationReturnIndex["Simulated Year"] == 10][
            "Simulated Investment Growth"
        ].max(),
    )
    investmentAtMin, investmentAtMax = (
        tidySimulationReturnIndex.loc[
            tidySimulationReturnIndex["Simulated Investment Growth"]
            == portfolioValueMin,
            "Investments",
        ].values[0],
        tidySimulationReturnIndex.loc[
            tidySimulationReturnIndex["Simulated Investment Growth"]
            == portfolioValueMax,
            "Investments",
        ].values[0],
    )
    listForAverage = []
    for i in range(11):
        avg = tidySimulationReturnIndex[
            tidySimulationReturnIndex["Simulated Year"] == i
        ]["Simulated Investment Growth"].mean()
        listForAverage.append([i, "Simulated Avg", avg.round(2)])
    avgDF = pd.DataFrame(
        listForAverage, columns=tidySimulationReturnIndex.columns.tolist()
    )

    simulationFig = px.line(
        tidySimulationReturnIndex,
        x="Simulated Year",
        y="Simulated Investment Growth",
        color="Investments",
        color_discrete_sequence=["#D3D3D3"],
        color_discrete_map={
            investmentAtMin: "#00b2e2",
            investmentAtMax: "#00b2e2",
            "Simulated Avg": "#f99e6b",
        },
    )
    simulationFig.add_trace(
        go.Scatter(
            x=avgDF["Simulated Year"],
            y=avgDF["Simulated Investment Growth"],
            mode="lines",
            name="Simulated Avg",
        )
    )
    for i, trace in enumerate(simulationFig.data):
        name = trace.name
        if name != "Simulated Avg":
            trace["showlegend"] = False
        else:
            continue
    simulationFig.update_traces(hovertemplate="USD %{y}")
    simulationFig.update_layout(
        {
            "height": 440,
            "paper_bgcolor": "var(--report_background_page)",
            "hovermode": "closest",
            "plot_bgcolor": "var(--report_background_page)",
            "legend_title_text": "",
        },
        legend=dict(
            y=-0.15,
            x=0.15,
        ),
    )

    #tidySimulationReturnIndex['Simulated Year'] = tidySimulationReturnIndex['Simulated Year']+1

    plotCorrelationDf = correlationPlotDf[
        df3.dropna()["Risk Asset Class"]
    ].reset_index()
    plotCorrelationDf = plotCorrelationDf[
        plotCorrelationDf["Index"].isin(df3.dropna()["Risk Asset Class"])
    ]  # .set_index('Index')

    (styles, legend) = discrete_background_color_bins(plotCorrelationDf,colorOption = 1)

    exp_ret = portMonteCarlo.mean()[0]
    twostddev = portMonteCarlo.mean()[0] * 2
    # Number of rows per page. Default settings mean that 28 rows fit nicely,
    # but this may change if other data is on the page.
    # rows_per_page = 15
    # Number of required pages
    # j = len(records) // rows_per_page + 1

    # Generate ddk pages of tabular data. The indexer picks the rows that fit between i and i+30, or
    # i and the max of the df if that does not fit.
    # table_pages = [
    #    make_page(
    #        records[
    #            i * rows_per_page : (i + 1) * rows_per_page
    #            if (i + 1) * rows_per_page <= len(records)
    #            else len(records)
    #        ],
    #        i,
    #        j,
    #        columns_table_two,
    #        clientName,
    #    )
    #    for i in range(j)
    # ]

    return ddk.Report(
        display_page_numbers=True,
        orientation="horizontal",
        children=[
            ddk.Page(
                [
                    html.Img(
                        src=app.get_asset_url("frontPageCover.jpg"),
                        style={"height": "100%"},
                    ),
                    ddk.Block(
                        [
                            html.H3(
                                "{}".format(reportName).upper(),
                                style={"fontSize": "28px"},
                            ),
                            html.H3(
                                " Prepared by {} ".format(financialAdvisor),
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            html.H3(
                                'Asset Allocation Analysis',
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            html.H3(
                                [
                                    ddk.Icon(icon_name="briefcase"),
                                    " Prepared for {} ".format(clientName),
                                ],
                                style={"marginTop": "2in", "fontSize": "28px"},
                            ),
                            html.H3(
                                "on {} ".format(createdTime[0:10]),
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                        ],
                        style={
                            "top": "40%",
                            "position": "absolute",
                            "color": "Gray",
                            "marginLeft": "1in",
                        },
                    ),
                    footer,
                ],
                style={
                    "backgroundColor": "White",
                    "color": "Gray",
                    #'background-size': '150px 100px',
                    #'background-image': 'url("/assets/adeppar_background.png")',
                },
                #                page_margin={
                #                    "top": "0in",
                #                    "bottom": "0in",
                #                    "left": "2.5in",
                #                    "right": "0in",
                #                },
            ),
            ddk.Page(
                [
                    ddk.Row(
                        style={"height": "7%"},
                        children=[
                            ddk.Block(
                                width=85,
                                children=html.H2("DISCLAIMERS"),
                            ),
                            ddk.Block(
                                width=15,
                                children=html.Img(
                                    src=app.get_asset_url("logo.png"),
                                    style={"height": "90%"},
                                ),
                            ),
                        ],
                    ),
                    html.P(
                        """
This presentation has been prepared solely for informational purposes and is not an offer, or a solicitation of an offer, to buy or sell any securities or products or to participate in any product or trading strategy. No sale of securities will be made in any jurisdiction in which the offer, solicitation, or sale is not authorized or to any person to whom it is unlawful to make the offer, solicitation, or sale. If any such offer of securities or products is made, it will be made pursuant to a definitive confidential offering document or other documentation which contains material information not contained herein and to which prospective investors will be referred.
The information in this presentation is not complete, does not contain certain material information about the products, including important disclosures and risk factors associated with an investment strategy and is qualified in its entirety by the information included in the confidential offering document or other documentation. Any decision to invest in such securities or products should be made solely in reliance upon such documentation and not this presentation.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "12px",
                        },
                    ),
                    html.P(
                        """
Where applicable, returns indicated as simulated do not represent the trading strategies, holdings, or performance of actual accounts, have some intrinsic limitations and should not be used as the sole basis informing any investment decisions or strategy.
Please see  additional disclaimers and notes at the bottom of each relevant page and end of the presentation; they are an integral part of this presentation.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "12px",
                        },
                    ),
                    html.P(
                        """
This presentation is not an advertisement for any products or services. It only serves the basis for a one-on-one discussion. 
Do not distribute this presentation without permission.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "12px",
                        },
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("Asset Allocation Review"),
                    ddk.Block(
                        width=55,
                        children=[sunburstFig],
                    ),
                    ddk.Block(
                        width=45,
                        margin=50,
                        children=[
                            ddk.DataTable(
                                id="table",
                                columns=columns_table_one,
                                data=summaryStatsDF.to_dict("records"),
                                editable=False,
                                fill_width=True,
                                style_as_list_view=True,
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": "Investment Amount"},
                                        "textAlign": "right",
                                        "fontWeight": "bold",
                                    },
                                    {
                                        "if": {"column_id": "Weight"},
                                        "textAlign": "right",
                                        "fontWeight": "bold",
                                    },
                                ],
                                style_cell={
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                    "textOverflow": "ellipsis",
                                    "textAlign": "left",
                                },
                                style_header={
                                    "backgroundColor": "white",
                                    "fontWeight": "bold",
                                },
                            )
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("ASSET ALLOCATION REVIEW"),
                    ddk.Block(
                        width=100,
                        children=[
                            html.H3(
                                "Asset Allocation Proxy Index Assumptions",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.DataTable(
                                id="returnTable",
                                columns=columns_table_three,
                                data=summaryStatsDF.round(3).to_dict("records"),
                                editable=False,
                                fill_width=True,
                                # style_as_list_view=True,
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
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                In this analysis we will simulate investment choices into unique asset classes using proxy indices. 
                                These proxy indices were reviewed by Insigneo's highly experienced Investment Committee. 
                                The proxy indices were chosen as representative for a diverse set of realistic investment options. With that said the indices are not actually investable assets.
                                Even a passive strategy tracking an index will exhibit tracking error. Additionally any fees on the strategy will further detract from returns and deviate from the index.
                                The strength of Insigneo's model portfolios lies in our approach. The Investment Committee ​​​​​​​mixes both qualitative and quantitative variables to produce strategies that can support a wide range of client objectives.
                                """,
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("Historical Review: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        children=[
                            html.H3(
                                "Historical Yearly Returns (%)",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            html.Div(historicalLegend, style={"float": "right"}),
                            ddk.DataTable(
                                data=heatmapDfPivot.round(2).to_dict("records"),
                                columns=[
                                    {"name": i, "id": i}
                                    for i in heatmapDfPivot.columns
                                ],
                                style_data_conditional=historicalStyles,
                                style_cell={
                                    "height": "auto",
                                    # all three widths are needed
                                    "minWidth": "7px",
                                    "width": "100px",
                                    "maxWidth": "100px",
                                    "whiteSpace": "normal",
                                    'fontSize':9,
                                },
                            ),
                        ],
                    ),ddk.Block(
                        width=99,
                        children=[
                            html.P(
                                """The performance data quoted represents past performance and does not guarantee future results. The investment return and principal value of an investment will
fluctuate; thus an investor's shares, when redeemed, may be worth more or less than their original cost. Current performance may be lower or higher than return
data quoted herein. For current performance data please contact your advisor.
Standardized Returns assume reinvestment of dividends and capital gains. They depict performance without adjusting for the effects of taxation and do not reflect actual investments but instead track broadly used indices.
If adjusted for taxation, the performance quoted could be significantly reduced. Additionally, these returns are before fees, fees would have detracted from historical performance.""",
                                style={"columnCount": 1},
                            )
                        ],
                    ),
                    footer,
                ]
            ),ddk.Page(
                [
                    make_header("Proposed Allocation Model Assumptions: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        margin=2,
                        children=[
                            html.H3(
                                "Risk and Return Analysis",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.Graph(
                                figure=px.scatter(
                                    historicalAssetAllocationStatsChart,
                                    y="Historical Yearly Mean Return",
                                    x="Historical Yearly Standard Deviation",
                                    color='Asset Class',
                                    size="Proposed Allocation",
                                    text="Risk Asset Class",
                                    color_discrete_map={
                "Equity": "#DFE0B9",
                "Fixed Income": "#505F9B",
                "Cash & Cash Equivalent": "#079BD3",
                "Alternative Investments": "#7B9B50",
            },
                                     #trendline="ols", trendline_options=dict(log_x=True)
                                )
                                .update_layout(
                                    {
                                        "paper_bgcolor": "var(--report_background_page)",
                                        "plot_bgcolor": "var(--report_background_page)",
                                    },
                                    legend=dict(
 yanchor="bottom",
 y=1.02,
)
                                )
                                .update_traces(textposition="top center"),
                                style={"height": 400},
                            )
                        ],
                    ),
                    ddk.Block(
                        width=99,
                        children=[
                            html.P(
                                """On the risk-return graphs, also known as scattergrams or scatterplots,
each point on the analysis represents both the return and risk of the proposal and
benchmarks. Risk, defined as standard deviation, is measured along the x-axis, while return
is measured along the y-axis. In general, anything plotted to
the northwest of another point on the graph is considered to have outperformed the other
on a risk-adjusted basis. Historical risk-adjusted performance is not a predictor of future
risk-adjusted performance. Data used in this and following historical analysis pages is from """+str(commonStartDate)+' to '+str(endDate)+' and does not include the impact of fees, fees would lower the historical returns',
                                style={"columnCount": 1},
                            )
                        ],
                    ),
                    footer,
                ]
            ),            
            ddk.Page(
                [
                    make_header("Historical Review: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.H3(
                                "Historical Performance Comparison",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.Graph(
                                figure=px.line(
                                    tidyhistoricalCumulativeReturnsDf.loc[
                                        tidyhistoricalCumulativeReturnsDf["Investments"]
                                        != "Proposed Allocation"
                                    ].loc[
                                        tidyhistoricalCumulativeReturnsDf["Investments"]
                                        != "Cash"
                                    ],
                                    x="Date",
                                    y="Historical Return",
                                    color="Investments",
                                )
                                .add_trace(
                                    go.Scatter(
                                        x=tidyhistoricalCumulativeReturnsDf.loc[
                                            tidyhistoricalCumulativeReturnsDf[
                                                "Investments"
                                            ]
                                            == "Proposed Allocation"
                                        ]["Date"],
                                        y=tidyhistoricalCumulativeReturnsDf.loc[
                                            tidyhistoricalCumulativeReturnsDf[
                                                "Investments"
                                            ]
                                            == "Proposed Allocation"
                                        ]["Historical Return"],
                                        name="Proposed Portfolio",
                                        line=dict(
                                            color="royalblue", width=8, dash="dash"
                                        ),
                                    )
                                )
                                .update_layout(
                                    {
                                        "paper_bgcolor": "var(--report_background_page)",
                                        "plot_bgcolor": "var(--report_background_page)",
                                    },legend=dict(
 yanchor="bottom",
 y=1.02,
),
                                )
,
                                style={"height": 400},
                            ),
                        ],
                    ),
                    ddk.Block(
                        width=99,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                The performance data designated as “Proposed Portfolio” on this page, the previous page and on each of the following pages of this proposal is intended to model what the return of a portfolio would have been
had you been invested in the investment risk asset class proxy indices, in the percentages proposed, over the time periods shown with scheduled rebalancing. These returns are hypothetical returns based
on a simulated account (not an actual account). Indices are not actually investable assets, even a passive investment strategy tracking an index will exhibit tracking error. Additionally, these returns are before fees, fees would have detracted from historical performance""",
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),ddk.Page(
                [
                    make_header("Historical Review: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        children=[
                            html.H3(
                                "Historical Annualized Returns",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.DataTable(
                                id="returnTable",
                                columns=columnsHistoricalAnnualized,
                                data=calculatedReturnDf.reset_index()
                                .round(4)
                                .to_dict("records"),
                                editable=False,
                                fill_width=True,
                                # style_as_list_view=True,
                                style_cell={
                                    "height": "auto",
                                    # all three widths are needed
                                    "minWidth": "10px",
                                    "width": "160px",
                                    "maxWidth": "160px",
                                    "whiteSpace": "normal",
                                },
                            ),
                        ],
                    ),
                    ddk.Block(
                        width=99,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                You would not necessarily have obtained these performance results if you held this portfolio for the periods indicated. Actual performance results of accounts vary due to factors such as timing of contributions and withdrawals, rebalancing schedules and the security and manager selection. Also, fees would apply to, and reduce the performance of, investment products included in this hypothetical portfolio. The selection of investment products in this proposal reflects the benefit of hindsight based on historical rates of return using indices.
                                A manager, even an index manager, may not generate the same returns as an index they track. This performance is presented for illustrative purposes only.
                                """,
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(#DIVIDER PAGE
                [
                    ddk.Block(
                        [
                            html.H3(
                                'Asset Allocation Model Expected Returns Before Fees',
                                style={"fontSize": "28px"},
                            ),
                            html.H3(
                                "Model expectations last updated on {} ".format(createdTime[0:10]),
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                        ],
                        style={
                            "top": "40%",
                            "position": "absolute",
                            "color": "Gray",
                            "marginLeft": "1in",
                        },
                    ),
                    footer,
                ],
                style={
                    "backgroundColor": "White",
                    "color": "Gray",
                    #'background-size': '150px 100px',
                    #'background-image': 'url("/assets/adeppar_background.png")',
                },
                #                page_margin={
                #                    "top": "0in",
                #                    "bottom": "0in",
                #                    "left": "2.5in",
                #                    "right": "0in",
                #                },
            ),
            ddk.Page(
                [
                    make_header("Proposed Allocation Model Assumptions: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        children=[
                            html.H3(
                                "Asset Class Modeling Assumptions",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.DataTable(
                                id="returnTable",
                                columns=columns_table_two,
                                data=summaryStatsDF.round(3).to_dict("records"),
                                editable=False,
                                fill_width=True,
                                style_as_list_view=True,
                                style_cell={
                                    "height": "auto",
                                    # all three widths are needed
                                    "minWidth": "10px",
                                    "width": "160px",
                                    "maxWidth": "160px",
                                    "whiteSpace": "normal",
                                    'fontSize':10,
                                },
                            ),
                        ],
                    ),
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                The expected return must be viewed as part of the description of the entire distribution (assuming a quadratic distribution). Viewed alone, it measures the mean of the entire
distribution of future outcomes. It may never be achieved as an outcome at all. The standard deviation portrays the dispersion of possible outcomes around the expected return.
To decide whether it makes sense to invest in an asset class, these elements must be viewed together, and compared with the nature of other asset classes. Each input viewed
alone is insufficient for solving the portfolio selection problem. Please see disclosures and disclaimers at the end of this presentation for more information.""",
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("Proposed Allocation Model Assumptions: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        margin=2,
                        children=[
                            html.H3(
                                "Model Expected Risk and Return Analysis",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            ddk.Graph(
                                figure=px.scatter(
                                    summaryStatsDF.loc[
                                        summaryStatsDF["Asset Class"]
                                        != "Cash & Cash Equivalent"
                                    ],
                                    y="Model Yearly Expected Return",
                                    x="Model Yearly Standard Deviation",
                                    color="Asset Class",
                                    size="Proposed Allocation",
                                    text="Sub Asset Class",
                                    color_discrete_map={
                "Equity": "#DFE0B9",
                "Fixed Income": "#505F9B",
                "Cash & Cash Equivalent": "#079BD3",
                "Alternative Investments": "#7B9B50",
            },
                                ).update_traces(textposition="top center")
                                .update_layout(
                                    {
                                        "paper_bgcolor": "var(--report_background_page)",
                                        "plot_bgcolor": "var(--report_background_page)",
                                    },
                                    legend=dict(
 yanchor="bottom",
 y=1.02,
)
                                )
                                .update_traces(textposition="bottom right"),
                                style={"height": 400},
                            )
                        ],
                    ),
                    ddk.Block(
                        width=99,
                        children=[
                            html.P(
                                """On the risk-return graphs, also known as scattergrams or scatterplots,
each point on the analysis represents both the return and risk of the proposal and
benchmarks. Risk, defined as standard deviation, is measured along the x-axis, while return
is measured along the y-axis. In general, anything plotted to
the northwest of another point on the graph is considered to have outperformed the other
on a risk-adjusted basis. Historical risk-adjusted performance is not a predictor of future
risk-adjusted performance. Data is this chart represents model based statistics. Model based statistics are an estimation of future return potential and should not be considered a guarantee.
Additionally the data is presented before fees. Fees will detract from expected retruns. 
                """,
                                style={"columnCount": 1},
                            )
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("Proposed Allocation Model Assumptions: Statistics Before Fees"),
                    ddk.Block(
                        width=100,
                        children=[
                            html.H3(
                                "Asset Class Model Correlation Matrix",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            html.Div(legend, style={"float": "right"}),
                            ddk.DataTable(
                                data=plotCorrelationDf.round(2).to_dict("records"),
                                columns=[
                                    {"name": i, "id": i}
                                    for i in plotCorrelationDf.columns
                                ],
                                style_data_conditional=styles,
                                style_cell={
                                    "height": "auto",
                                    # all three widths are needed
                                    "minWidth": "7px",
                                    "width": "100px",
                                    "maxWidth": "100px",
                                    "whiteSpace": "normal",
                                    'fontSize':9,
                                },
                            ),
                        ],
                    ),
                    ddk.Block(
                        width=99,
                        children=[
                            html.P(
                                """Correlation refers to the degree to which investments within a portfolio share similar risk and return characteristics. 
                                A portfolio bearing assets that are highly correlated is less diversified. As a result, high correlation is associated with greater risk in the form of volatility. 
                                By contrast, the more diversified a portfolio is, the lower the correlation of its underlying assets, reflected as lower volatility. 
                                Investments can even be negatively correlated, which means they exhibit characteristics that tend to make them perform inversely to one another.
                                In this table risk asset classes that are more highly correlated with each other have a bolder color. The correlation matrix is used to calcualte the 
                                portfolio's model standard deviation. Portfolio Standard Deviation is calculated based on the standard deviation of returns of each asset in the portfolio, the proportion of each asset in the overall portfolio i.e., their respective weights in the total portfolio, and also the correlation between each pair of assets in the portfolio.
                                """,
                                style={"columnCount": 1},
                            )
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("Proposed Allocation Review: Simulation Before Fees"),
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.H2(
                                "Monte Carlo Simulated Portfolio Statistics",
                                style={"marginTop": ".1in", "fontSize": "18px"},
                            ),
                            html.H3(
                                "Mean annualized return: {:.2f}%".format(
                                    portMonteCarlo.mean()[0]
                                ),
                                style={"marginTop": ".1in", "fontSize": "14px"},
                            ),
                            html.H3(
                                "Annualized standard Deviation: {:.2f}%".format(
                                    portMonteCarlo.std()[0]
                                ),   
                                style={"marginTop": ".01in", "fontSize": "14px"},
                            ),
                            ddk.Graph(
                                figure=px.histogram(
                                    portMonteCarlo,
                                    x="Proposal Simulated Return Distribution",
                                ).add_shape(
                                    type="line",
                                    yref="paper",
                                    y1=5,
                                    y0=0,
                                    x0=exp_ret,
                                    x1=exp_ret,
                                    line=dict(color="white", width=2, dash="dash"),
                                )
                                .add_shape(
                                    type="line",
                                    yref="paper",
                                    y1=5,
                                    y0=0,
                                    x0=exp_ret - portStandardDeviation,
                                    x1=exp_ret - portStandardDeviation,
                                    line=dict(color="white", width=2, dash="dash"),
                                )
                                .add_shape(
                                    type="line",
                                    yref="paper",
                                    y1=5,
                                    y0=0,
                                    x0=exp_ret + portStandardDeviation,
                                    x1=exp_ret + portStandardDeviation,
                                    line=dict(color="white", width=2, dash="dash"),
                                )
                                .add_shape(
                                    type="line",
                                    yref="paper",
                                    y1=5,
                                    y0=0,
                                    x0=exp_ret + 2 * portStandardDeviation,
                                    x1=exp_ret + 2 * portStandardDeviation,
                                    line=dict(color="white", width=2, dash="dash"),
                                )
                                .add_shape(
                                    type="line",
                                    yref="paper",
                                    y1=5,
                                    y0=0,
                                    x0=exp_ret - 2 * portStandardDeviation,
                                    x1=exp_ret - 2 * portStandardDeviation,
                                    line=dict(color="white", width=2, dash="dash"),
                                )
                                .update_layout(
                                    hovermode="x unified",
                                )
                                .update_traces(
                                    hovertemplate="%{y} counts",
                                ),
                                style={"height": 380},
                            ),
                        ],
                    ),
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                The simulation draws random samples from a normal (Gaussian) distribution. The function has its peak at the mean, and its “spread” increases with the standard deviation (the function reaches 0.607 times its maximum at mean plus standard deviation and mean minus standard deviation). This implies that normal is more likely to return samples lying close to the mean, rather than those far away
                                using NumPy's random.Generator. NumPy is an open source project aiming to enable numerical computing with Python. It was created in 2005, building on the early work of the Numeric and Numarray libraries. NumPy will always be 100% open source software, free for all to use and released under the liberal terms of the modified BSD license.
                                Inherent in any investment is the potential for loss. THIS SIMULATION IS BEFORE FEES; FEES WILL DETRACT FROM EXPECTED RETURNS. 
                                """,
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    make_header("PROPOSED ALLOCATION REVIEW: SIMULATION Before Fees"),
                    ddk.Block(
                        width=100,
                        margin=5,
                        children=[
                            html.H3(
                                "Simulated Growth of $100k over a 10 year investment period",
                                style={"marginTop": ".05in", "fontSize": "18px"},
                            ),
                            html.H3(
                                "High simulated ending portfolio value: ${:,.0f}".format(
                                    tidySimulationReturnIndex.loc[
                                        tidySimulationReturnIndex[
                                            "Simulated Investment Growth"
                                        ]
                                        == portfolioValueMax,
                                        "Simulated Investment Growth",
                                    ].values[0]
                                ),
                                style={"fontSize": "10px"},
                            ),
                            html.H3(
                                "Average simulated ending portfolio value: ${:,.0f}".format(
                                    avgDF[
                                            "Simulated Investment Growth"
                                        ].values[10]
                                ),
                                style={"fontSize": "10px"},
                            ),
                            html.H3(
                                "Low simulated ending portfolio value: ${:,.0f}".format(
                                    tidySimulationReturnIndex.loc[
                                        tidySimulationReturnIndex[
                                            "Simulated Investment Growth"
                                        ]
                                        == portfolioValueMin,
                                        "Simulated Investment Growth",
                                    ].values[0]
                                ),
                                style={"fontSize": "10px"},
                            ),
                            ddk.Graph(
                                figure=simulationFig,
                            ),],
                    ),
                    ddk.Block(
                        width=99,
                        margin=5,
                        children=[
                            html.P(
                                """ 
                                Using a similar technique as before we take twenty random draws from a representative distribution of expected yearly returns to represent a twenty year investment horizon and plot the impied growth of an initial investment of 100k BEFORE FEES. FEES WILL DETRACT FROM EXPECTED PERFORMANCE. 
                                Portfolios with higher risk, as measured by standard deviation will have a much wider distribution of simulated returns. Please note that all investing is subject to risk and could lead to a partial or total loss of capital.
                                """,
                                style={"columnCount": 1},
                            ),
                        ],
                    ),
                    footer,
                ]
            ),
        ]
        # + table_pages
        + addDisclaimers(businessType)
        + [
            ddk.Page(
                [
                    ddk.Row(
                        style={"height": "7%"},
                        children=[
                            ddk.Block(
                                width=85,
                                children=html.H2("DISCLAIMERS"),
                            ),
                            ddk.Block(
                                width=15,
                                children=html.Img(
                                    src=app.get_asset_url("logo.png"),
                                    style={"height": "90%"},
                                ),
                            ),
                        ],
                    ),
                    html.P(
                        """
                Important Disclosures and Disclaimers: This material is distributed for informational purposes only and intended solely for Insigneo Advisory Services, LLC, (“IAS” or “Insigneo”) an Securities Exchange
Commission (“SEC”) investment adviser’s clientele, potential customers, and/or other parties to whom Insigneo chooses to share such information. The discussions and opinions in this document (or
“Factsheet”) are intended for general informational purposes only, and are not intended to provide investment advice and there is no guarantee that the opinions expressed herein will be valid beyond the
date of this document. The information presented in this Factsheet pertains to certain investments related to Insigneo’s I-Maps Conservative Plus Portfolio Strategy (“Conservative Plus Portfolio”). It is not
intended to be used as a general guide to investing, or as a source of any specific recommendation, and makes no implied or expressed recommendations concerning the manner in which clients’ accounts
should or would be handled, as appropriate strategies depend on the client’s specific objectives. This does not constitute an offer or solicitation with respect to the purchase or sale of any security in any
jurisdiction in which such an offer or solicitation is not authorized or to any person to whom it would be unlawful to make such an offer or solicitation. This material is based upon information which we
considerto be reliable, but we do not represent that suchinformationis accurate or complete, and it should not be relied upon as such. Any historical informationis as of the date stated.
This Factsheet may include forward-looking statements and all statements other than statements of historical fact are to be considered forward-looking and subjective (including words such as “believe,”
“estimate,” “anticipate,” “may,” “will,” “should,” and “expect”). Although Insigneo believes that the expectations reflected in such forward-looking statements are reasonable, it can provide no assurance that
such expectations will prove to be correct. Many factors including changing market conditions and global political and economic events could cause actual outcomes, results, or performance to differ
materially from those discussed in such forward-looking statements. Insigneo shall not be responsible for the consequences of reliance upon any opinion or statements contained herein, and expressly
disclaims any liability, including incidental or consequential damages, arising from any errors, omissions, or misuse.""",
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
                Model/Hypothetical Performance Results: The performance results included in the report are hypothetical returns which have
been compiled by IAS. Returns on this slide reflects the reinvestment of income and dividends, but do not take into account trading costs, management fees, and any other applicable fees and expenses.
Hypothetical performance results may have inherent limitations, some of which are described below. A client’s actual return will be reduced by the advisory fees and any other expenses which may be
incurred in the management of an investment advisory account. See Part 2A of the IAS’ Form ADV for a complete description of the investment advisory fees customarily charged. No representation is
being made that any account will or is likely to achieve profits or losses similar to those shown. Hypothetical performance are prepared with the benefit of hindsight and there are numerous other factors
related to the markets in general or to the implementation of any specific trading strategy which cannot be fully accounted for in the preparation of hypothetical performance results and all of which can
adversely affect actual trading results. The hypothetical results do not represent actual recommendations or trading and may not reflect the impact that material economic and market factors might have
had on IAS’ decision-making if the IAS were actually managing client’s money. During the period shown, IAS was not managing client accounts according to the strategy depicted. IAS model portfolios are
provided for illustrative purposes only and do not take into account the particular financial circumstances, objectives, risk tolerances, goals or other needs of any specific client. IAS model portfolios do not
take into account all possible variations which may alter the risks associated with any strategy. Model portfolio assumptions may change and a client’s actual portfolio and investment objective(s) for
accounts managed by IAS may look significantly differentfrom IAS models when deemed appropriate. No representation is being made that a client will achieve similarresults to those shown herein.""",
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
                While taken from sources deemed to be accurate, Insigneo makes no representations regarding the accuracy of the information in this document and certain information is based on third-party sources
believed to be reliable, but has not been independently verified and its accuracy or completeness cannot be guaranteed. The results portrayed are estimated, unaudited and subject to adjustment. Also,
the net results reflect the reinvestment of dividends and other earnings and the deduction of costs of execution and management fees. Particular investors’ returns will vary from the historical performance
due various factors including, but not limited to timing of withdrawals and start date in using the referenced strategy. Past performance is no indication of future results. Inherent in any investment is the
potential for loss. All information is provided for informational purposes only and should not be deemed as a recommendation to buy the securities mentioned. A complete listing of all investments and
performance by Insigneo is available upon request.""",
                        style={
                            "margin-Bottom": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
                This material is intended only to facilitate general discussions and is not intended as a source of any specific recommendation for a specific individual.Please consult with your account executive or financial advisor if any specific recommendation made herein is right for you.This does not constitute an offer or solicitation with respect to the purchase or sale of any security in any jurisdiction in which such an offer orsolicitation is not authorized or to any person to whom it would be unlawful to make such an offer or solicitation. Brokerage and investment advisoryaccount investments are subject to market risk including loss of principal.
                Insigneo Securities, LLC (Insigneo)) is a broker/dealer registered with the U.SSecurities and Exchange Commission (SEC) and a member of the Financial Industry Regulatory Authority (FINRA) and Securities Investors Protection Corporation (SIPC). Insigneo is affiliated to two U.S. registered investment advisors, Insigneo Wealth Advisors, LLC (IWA) and Insigneo AdvisoryServices, LLC (IAS). Collectively, we refer to Insigneo, IAS, and IWA as the Insigneo Financial Group. To learn more about their business, including theirconflicts of interest and compensation practices for the Broker Dealer please go to www.insigneo.com/en/disclosures and any conflicts related to their advisory services, please see their Form ADV and brochure which can be found at Investment Advisor Public Disclosure website (https://adviserinfo.sec.gov/).
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    ddk.Row(
                        style={"height": "7%"},
                        children=[
                            ddk.Block(
                                width=85,
                                children=html.H2("DISCLAIMERS"),
                            ),
                            ddk.Block(
                                width=15,
                                children=html.Img(
                                    src=app.get_asset_url("logo.png"),
                                    style={"height": "90%"},
                                ),
                            ),
                        ],
                    ),
                    html.P(
                        """
                This material is distributed for informational purposes only and intended solely for Insigneo Advisory Services, LLC, (“IAS” or “Insigneo”) an Securities Exchange Commission(“SEC”) investment adviser’s clientele, potential customers, and/or other parties to whom Insigneo chooses to share such information.  The discussions and opinions in this document (or “Presentation”) are intended for general informational purposes only, and are not intended to provide investment advice and there is no guarantee that the opinionsexpressed herein will be valid beyond the date of this document.
                The information presented in this Presentation is not intended to be used as a general guide to investing, or as asource of any specific recommendation, and makes no implied or expressed recommendations concerning the manner in which clients’ accounts should or would be handled, asappropriate strategies depend on the client’s specific objectives.  This does not constitute an offer or solicitation with respect to the purchase or sale of any security in anyjurisdiction in which such an offer or solicitation is not authorized or to any person to whom it would be unlawful to make such an offer or solicitation.  This material is basedupon information which we consider to be reliable, but we do not represent that such information is accurate or complete, and it should not be relied upon as such.  Anyhistorical information is as of the date stated.This Presentation may include forward-looking statements and all statements other than statements of historical fact are to be considered forward-looking and subjective(including words such as “believe,” “estimate,” “anticipate,” “may,” “will,” “should,” and “expect”).  Although Insigneo believes that the expectations reflected in such forward-looking statements are reasonable, it can provide no assurance that such expectations will prove to be correct.  Many factors including changing market conditions and globalpolitical and economic events could cause actual outcomes, results, or performance to differ materially from those discussed in such forward-looking statements.  Insigneo shallnot be responsible for the consequences of reliance upon any opinion or statements contained herein, and expressly disclaims any liability, including incidental or consequentialdamages, arising from any errors, omissions, or misuse.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
                Index Comparisons and Benchmarks: The volatility of the portfolio (strategy) may be materially different from the individual performance attained by a specific investor. In addition, the strategy holdings
may differ significantly from the securities that comprise the indices or benchmarks referenced in this material. The indices have not been selected to represent an appropriate benchmark to compare an
investor’s performance, but rather are disclosed to allow for comparison of the portfolio strategy’s performance to that of certain well-known and widely recognized indices. You cannot invest directly in an
index. This material includes the following indices and benchmarks: (i) Bloomberg Barclays US Aggregate, (ii) Bloomberg Barclays US Corp HY Total Return, (iii) Bloomberg Barclays EM USD Agg Total
Return; (iv) MSCI ACWI; (v) ICE Libor 1-month USD; (vi) UST Bill 3 Month MM Yield; and (vii) LBMA Gold Price PM USD. The Bloomberg Barclays US Total Return Index measures the investment grade, fixedrate, taxable bond market. The index includes Treasuries, government-related and corporate securities, MBS (agency fixed-rate and hybrid ARM pass-through), ABS and CMBS (agency and non-agency).
The Bloomberg Barclays US Corporate High Yield Bond Index measures the USD-denominated, high yield, fixed-rate corporate bond market. Securities are classified as high yield if the middle rating of
Moody's, Fitch and S&P is Ba1/BB+/BB+ or below. Bonds from issuers with an emerging markets country of risk, based on Barclays EM country definition, are excluded. The Bloomberg Barclays Emerging
Markets Hard Currency Aggregate Index is a flagship hard currency Emerging Markets debt benchmark that includes USD-denominated debt from sovereign, quasi-sovereign, and corporate EM issuers.
The MSCI ACWI captures large and mid-cap representation across 23 Developed Markets (DM) and 26 Emerging Markets (EM) countries*. With 2,852 constituents, the index covers approximately 85% of
the global investable equity opportunity set. ICE LIBOR (also known as LIBOR) is a widely-used benchmark for short-term interest rates. The LIBOR methodology is designed to produce an average rate
that is representative of the rates at which large, leading internationally active banks with access to the wholesale, unsecured funding market could fund themselves in such market in particular currencies
for certain tenors. The 3 Month Treasury Bill Rate is the yield received for investing in a government issued treasury security that has a maturity of 3 months. The London bullion market is a wholesale overthe-counter market for the trading of gold and silver. Trading is conducted amongst members of the London Bullion Market Association (LBMA), loosely overseen by the Bank of England. Most of the
members are major international banks or bullion dealers and refiners. Any statements regarding future events constitute only subjective views or beliefs, are not guarantees or projections of performance,
should not be relied on, are subject to change due to a variety of factors, including fluctuating market conditions, and involve inherent risks and uncertainties, both general and specific, many of which
cannot be predicted or quantified and are beyond our control. Future results could differ materially and no assurance is given that these statements are now or will prove to be accurate or complete in any
way.""",
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    footer,
                ]
            ),
            ddk.Page(
                [
                    ddk.Row(
                        style={"height": "7%"},
                        children=[
                            ddk.Block(
                                width=85,
                                children=html.H2("DISCLAIMERS"),
                            ),
                            ddk.Block(
                                width=15,
                                children=html.Img(
                                    src=app.get_asset_url("logo.png"),
                                    style={"height": "90%"},
                                ),
                            ),
                        ],
                    ),
                    html.P(
                        """
                While taken from sources deemed to be accurate, Insigneo makes no representations regarding the accuracy of the information in this document and certain information is
based on third-party sources believed to be reliable, but has not been independently verified and its accuracy or completeness cannot be guaranteed. The results portrayed are
estimated, unaudited and subject to adjustment. Also, the net results reflect the reinvestment of dividends and other earnings and the deduction of costs of execution and
management fees. Particular investors’ returns will vary from the historical performance due various factors including, but not limited to timing of withdrawals and start date in
using the referenced strategy. Past performance is no indication of future results. Inherent in any investment is the potential for loss. All information is provided for
informational purposes only and should not be deemed as a recommendation to buy the securities mentioned. A complete listing of all investments and performance by
Insigneo is available upon request.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
Conflicts of Interest: Insigneo or Insigneo Financial Group, unless the specific context otherwise requires, typically and collectively refers to the Financial Industry Regulatory
Authority (”FINRA”) member broker dealer, Insigneo Securities, LLC and two affiliated Securities Exchange Commission (“SEC”) investment advisers, Insigneo Wealth Advisors,
LLC and Insigneo Advisory Services, LLC. Security products are offered and conducted through Insigneo Securities, LLC and advisory products and services are offered through
Insigneo Wealth Advisors, LLC or Insigneo Advisory Services, LLC. The referenced entities are under common ownership and share certain employees and office arrangements.
Investment advisory representatives of IAS are dually associated with affiliated entities and receive additional compensation related to advisory activities, which creates a
disclosable conflict. Please see IAS’ Form ADV Part 2A “Brochure” and your individual advisory representatives Form ADV Part 2B “Supplement” for further details.
This information is highly confidential and intended for review by the recipient only. The information should not be disseminated or be made available for public use or to any
other source without the express written authorization of Insigneo. Distribution of this document is prohibited in any jurisdiction where dissemination of such documents may be
unlawful. Please contact your investment adviser, accountant, and/or attorney for advice appropriate to your specific situation.
This information is highly confidential and intended for review by the recipient only. The information should not be disseminated or be made available for public use or to any
other source without the express written authorization of Insigneo. Distribution of this document is prohibited in any jurisdiction where dissemination of such documents may be
unlawful. Please contact your investment adviser, accountant, and/or attorney for advice appropriate to your specific situation.
Gross of fees performance: Performance results do not reflect the deduction of investment advisory fees and other expenses. Actual performance results will be reduced by
the investment advisory fees and expenses that you would pay. For example, if $100,000 were invested and experienced a 4% annual return compounded monthly for 10 years,
its ending value, without giving effect to the deduction of advisory fees, would be $149,083 with a compounded annual return of 4.07%. If an advisory fee of 0.25% of the
average market value of the account were deducted monthly for the 10-year period, the compounded annual return would be 3.82% and the ending dollar value would be
$145,414. For a description of all fees, costs and expenses, please refer to Insigneo’s Form ADV Part 2A, which is available upon request. The figures refer to the past and past
performance is not a reliable indicator of future results.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    html.P(
                        """
Hypothetical (simulated) performance: The performance forecasted is hypothetical, or back-tested performance. It is not actual performance. This performance is for
illustrative purposes only, and should not be used to predict future performance. Performance shown is based on current asset allocations, which may not represent past asset
allocations had these portfolios existed during the time periods shown. Asset allocations are subject to change without notice. Past performance is no guarantee of future performance. Hypothetical performance results have certain inherent limitations. They include: 1) They are prepared with the benefit of hindsight; 2) Unlike an actual performance record,
these results do not represent actual investment performance or trading and do not demonstrate Insigneo’s ability to manage money; 3) Insigneo did not recommend the
models used in the hypothetical portfolios for any clients during the period shown, and no clients invested money in accounts offered by Insigneo in accordance with those
strategies; 4) The results actual clients might have achieved would have differed from those shown because of differences in market conditions and in the timing and amounts of
their investments; and 5) Because the trades were not actually executed, the results may have under- or over-compensated for the impact, if any, of certain market factors, such
as the effect of limited trading liquidity. No representation is made that any client will or is likely to achieve profits or losses similar to those shown.
Diversification strategies do not ensure a profit and do not protect against losses in declining markets.
                """,
                        style={
                            "marginTop": ".01in",
                            "fontSize": "10px",
                        },
                    ),
                    ddk.Row(
                        [
                            html.P(
                                """
                Insigneo Advisory Services, LLC
777 Brickell Avenue
10th Floor
Miami, FL 33131
(P)(305) 373-9000
(Email) compliance_advisory@insigneo.com
                """,
                                style={
                                    "columnCount": 1,
                                    "marginTop": ".05in",
                                    "fontSize": "12px",
                                    "font-weight": "bold",
                                },
                            )
                        ]
                    ),
                    footer,
                ]
            ),
        ]
    )
