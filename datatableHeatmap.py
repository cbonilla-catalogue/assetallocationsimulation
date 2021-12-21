from dash import html

#https://learnui.design/tools/data-color-picker.html#single
#https://hihayk.github.io/scale/#2/8/50/80/-51/67/20/14/7C92FE/124/47/254/white

customColorScale = ['#ffe3ed','#ffecf3','#fff6f9','#ffffff','#f1f8e2','#e2f0c5','#d3e9a8']
customColorScaleDiverging = ['#ffe3ed','#ffecf3','#fff6f9','#ffffff','#f1f8e2','#e2f0c5','#d3e9a8']
customColorScaleSingleHue = ['#ffffff','#f8fbf0','#f1f8e2','#eaf4d3','#e2f0c5','#dbedb6','#d3e9a8']
customColorScale = [customColorScaleDiverging,customColorScaleSingleHue]

def discrete_background_color_bins(df, n_bins=7, columns='all',colorOption = 0):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        #backgroundColor = colorlover.scales[str(n_bins)]['seq'][colorPalette][i - 1]
        backgroundColor = customColorScale[colorOption][i - 1]
        color = 'inherit'# 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            },
            )
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))