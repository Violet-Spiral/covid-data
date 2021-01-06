import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
from numpy import cbrt
import matplotlib.pyplot as plt


DATA_URL = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'
full_df = pd.read_csv(DATA_URL,
                    parse_dates=['Date'],
                    encoding="ISO-8859-1",
                    dtype={"RegionName": str,
                            "RegionCode": str,
                            "CountryName": str,
                            "CountryCode": str},
                        usecols = ['Date','CountryName','RegionName',
                                'ConfirmedCases','ConfirmedDeaths','Jurisdiction'],
                    error_bad_lines=False)
full_df = full_df.set_index('Date', drop=True)

unique_countries = full_df['CountryName'].unique()

def graph_prediction(df, country='United States',
                    state=None, prediction='ConfirmedCases', window=30):
    

    if prediction not in ['ConfirmedCases','ConfirmedDeaths']:
        prediction = 'ConfirmedCases'

    if state in full_df['RegionName'].dropna().unique():
        df = full_df[(full_df['Jurisdiction'] == 'STATE_TOTAL') 
                    & (full_df['RegionName'] == state)][:-1]
    else: 
        df = full_df[(full_df['Jurisdiction'] == 'NAT_TOTAL') 
                    & (full_df['CountryName'] == country)][:-1]
    df = df[[prediction]]
    df = df.interpolate(method='time', limit_direction='forward', 
                        limit_area='inside', downcast='infer')
    df.index.freq = 'D'

    df = df[df[prediction] > 0]

    cbrt_df = cbrt(df)
    model = SARIMAX(cbrt_df, order = (0,2,0), seasonal_order = (3,2,1,7), 
                                        freq = 'D')
    fit_model = model.fit(max_iter = 200, disp = False)
    yhat = fit_model.forecast(window)**3

    pred_start = yhat.index.date.min()
    pred_end = yhat.index.date.max()
    true_start = df.index.date.min()
    true_end = df.index.date.max()

    if state in full_df['RegionName'].dropna().unique():
        title = f'{window} Day Forecast of Cumulative COVID-19 Cases in {state}, {country}'
    else:
        title = f'{window} Day Forecast of Cumulative COVID-19 Cases in {country}'
    fig = go.Figure(
                    data=[go.Scatter(x=df.index, y=df[prediction],
                                    name = 'Historical Cases')],
                    layout_title_text = title,
                    )
    fig.add_trace(go.Scatter(x=yhat.index, y=yhat.values,
                            name='Predicted Cases'))
    return fig

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
unique_states = []

app.layout = html.Div([
    html.H2('Hello World'),
    html.H4('Country'),
    dcc.Dropdown(
        id='dropdown_country',
        options=[{'label': i, 'value': i} for i in unique_countries],
        value='Select a country'
    ),
    html.Div(id='country_value'),
    html.H4('State'),
    dcc.Dropdown(
        id='dropdown_state',
        options=[{'label': i, 'value': i} for i in unique_states],
        value='Select a state'
    ),
    html.Div(id='state_value'),
    dcc.Graph(id='graph', figure=graph_prediction(full_df))

])


@app.callback(dash.dependencies.Output('country_value', 'children'),
              [dash.dependencies.Input('dropdown_country', 'value')])
def display_value(country_value):
    global unique_states
    unique_states = full_df[full_df['CountryName']
                            == country_value]['RegionName'].unique()
    return unique_states


# @app.callback(dash.dependencies.Output('state_value', 'children'),
#             [dash.dependencies.Input('dropdown_country', 'value')])
# def state_list(country):
#     return full_df[full_df['CountryName'] == country_value].unique()

if __name__ == '__main__':
    app.run_server(debug=True)
