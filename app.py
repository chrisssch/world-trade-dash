__author__ = "Christoph Schauer"

# imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


# load and prepare data
df = pd.read_csv('data/world_trade_extract.csv')

# reporter selector options
reporters = df.REPORTER.unique()
reporters.sort()
reporter_options = [{'label': e, 'value': e} for e in reporters]

# year selector options
years = df.YEAR.unique()
years.sort()
year_options = {int(e): str(e) for e in years}


app = dash.Dash()

app.layout = html.Div([

    # title
    html.Div([
        html.H1('Intra-EU Trade'),
        html.P('A little project for practicing Plotly Dash (work-in-progress)'),
    ],
    style={'textAlign': 'center'}
    ),
    
    # filter
    html.Div([
        html.Div([
            html.P('Select Reporting Country'),
            dcc.Dropdown(
                id='reporter-selector',
                options=reporter_options,
                value='Austria'
            )
        ],
        style={'width': '15%', 'display': 'inline-block', 'margin': 10, 'paddingRight': 50}
        ),
        html.Div([ 
            html.P('Select Year'),
            dcc.RangeSlider(
                id='year-selector',
                min=min(year_options.keys()), 
                max=max(year_options.keys()), 
                marks=year_options,
                value=[2017, 2019]
            )
        ],
        style={'width': '45%', 'display': 'inline-block', 'margin': 10}
        )
    ],
    style={'border': '1px lightgrey solid', 'margin': 10}
    ),

    # print out applied filters
    html.Div([
        html.H3(id='selected-filters')
    ], 
    style={'textAlign': 'center', 'margin': 10}
    ),

    # bar chart
    html.Div([
        dcc.Graph(id='bar-partners')
    ],
    style={'border': '1px lightgrey solid', 'margin': 10}
    ),

    # pie charts and line chart
    html.Div([
        html.Div([
            dcc.Graph(id='pie-products-1')
        ],
        style={'width': '28%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Graph(id='pie-products-2')
        ],
        style={ 'width': '28%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Graph(id='line-ts')
        ],
        style={'width': '40%', 'display': 'inline-block', 'float': 'right', 'margin': 10}
        )
    ],
    style={'border': '1px lightgrey solid', 'margin': 10},
    )
],

style={'fontFamily': 'helvetica', 'border': '1px lightgrey solid', 'margin': 10, 'padding': 10,}
)


# text: selected filters
@app.callback(
    Output('selected-filters', 'children'),
    [Input('reporter-selector', 'value'), Input('year-selector', 'value')]
)
def update_show(sel_reporter, sel_year_range):
    return f'Reporting Country: {sel_reporter}, Years: {sel_year_range[0]}-{sel_year_range[1]}'


# bar chart: trade flow by partner
@app.callback(
    Output('bar-partners', 'figure'),
    [Input('reporter-selector', 'value'), Input('year-selector', 'value')]
)
def update_bar(sel_reporter, sel_year_range):   
    #  filter, aggregate, and process data
    dfx = df[(df.REPORTER == sel_reporter) & (df.YEAR >= sel_year_range[0]) & (df.YEAR <= sel_year_range[1])]
    dfx = dfx[['PARTNER', 'IMPORTS_MN', 'EXPORTS_MN']].groupby(['PARTNER']).sum().reset_index()
    
    traces = [
        go.Bar(
            x=dfx.PARTNER,
            y=dfx.IMPORTS_MN,
            name='Imports (mn)'
        ),
        go.Bar(
            x=dfx.PARTNER,
            y=dfx.EXPORTS_MN,
            name='Exports (mn)'
        )
    ]
    layout = go.Layout(
        title=f'Trade by Partner ({sel_reporter}, {sel_year_range[0]}-{sel_year_range[1]})',
        xaxis={'title': 'Partner'},
        yaxis={'title': 'Trade Volumne (mn)'}
    )

    return {'data': traces, 'layout': layout}


# pie charts: trade flow by product
@app.callback(
    Output('pie-products-1', 'figure'),
    [Input('reporter-selector', 'value'), Input('year-selector', 'value')]
)
def update_pie_1(sel_reporter, sel_year_range):   

    dfx = df[(df.REPORTER == sel_reporter) & (df.YEAR >= sel_year_range[0]) & (df.YEAR <= sel_year_range[1])]
    dfx = dfx[['HS2', 'HS2_NAME', 'IMPORTS_MN']].groupby(['HS2', 'HS2_NAME']).sum().reset_index()
    dfx = dfx.sort_values(by='IMPORTS_MN', ascending=False)
    other = [999, 'OTHER', dfx.iloc[11:]['IMPORTS_MN'].sum()]
    dfx = dfx.iloc[:10]
    dfx.loc[-1] = other
    dfx['HS2_NAME_CUT'] = dfx.HS2_NAME.apply(lambda x: x[:32]+'...' if len(x) > 32 else x[:32])

    traces = [
        go.Pie(
            labels=dfx.HS2_NAME_CUT,
            values=dfx.IMPORTS_MN,
            textinfo='percent',
            hole=0.2
        )
    ]
    layout = go.Layout(
        title=f'Imports by Product Category (HS2) ({sel_reporter}, {sel_year_range[0]}-{sel_year_range[1]})'
    )
    return {'data': traces, 'layout': layout}


# pie charts: trade flow by product
@app.callback(
    Output('pie-products-2', 'figure'),
    [Input('reporter-selector', 'value'), Input('year-selector', 'value')]
)
def update_pie_2(sel_reporter, sel_year_range):   

    dfx = df[(df.REPORTER == sel_reporter) & (df.YEAR >= sel_year_range[0]) & (df.YEAR <= sel_year_range[1])]
    dfx = dfx[['HS2', 'HS2_NAME', 'EXPORTS_MN']].groupby(['HS2', 'HS2_NAME']).sum().reset_index()
    dfx = dfx.sort_values(by='EXPORTS_MN', ascending=False)
    other = [999, 'OTHER', dfx.iloc[11:]['EXPORTS_MN'].sum()]
    dfx = dfx.iloc[:10]
    dfx.loc[-1] = other
    dfx['HS2_NAME_CUT'] = dfx.HS2_NAME.apply(lambda x: x[:32]+'...' if len(x) > 32 else x[:32])

    traces = [
        go.Pie(
            labels=dfx.HS2_NAME_CUT,
            values=dfx.EXPORTS_MN,
            textinfo='percent',
            hole=0.2
        )
    ]
    layout = go.Layout(
        title=f'Exports by Product Category (HS2) ({sel_reporter}, {sel_year_range[0]}-{sel_year_range[1]})'
    )
  
    return {
        'data': traces,
        'layout': layout
    }


# line chart: trade flow by year
@app.callback(
    Output('line-ts', 'figure'),
    [Input('reporter-selector', 'value')]
)
def update_ts(sel_reporter):   

    dfx = df[df.REPORTER == sel_reporter]
    dfx = dfx[['YEAR', 'IMPORTS_MN', 'EXPORTS_MN']].groupby(['YEAR']).sum().reset_index()

    traces = [
        go.Scatter(
            x=dfx.YEAR,
            y=dfx.IMPORTS_MN,
            mode='lines',
            name='Imports (mn)'
        ),
        go.Scatter(
            x=dfx.YEAR,
            y=dfx.EXPORTS_MN,
            mode='lines',
            name='Exports (mn)'
        ),
    ]
    layout = go.Layout(
        title=f'Trade Flows by Year ({sel_reporter})',
        xaxis={'nticks': len(year_options)},
        yaxis={'title': 'Trade Volumne (mn)'}
    )

    return {
        'data': traces,
        'layout': layout
    }


if __name__ == '__main__':
    app.run_server()
