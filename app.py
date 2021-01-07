import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
from numpy import cbrt
from src import *

# get data
full_df = get_covid_data()
unique_countries = full_df['CountryName'].unique()

# set initial app settings
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# display layout and components
app.layout = html.Div([
    html.H2('COVID-19 Cumulative Infections Prediction'),
    html.H4('To Predict'),
    dcc.Dropdown(
        id='dropdown-prediction',
        options=[{'label':i,'value':i} for i in ['ConfirmedDeaths','ConfirmedCases']]
    ),
    html.H4('Country'),
    dcc.Dropdown(
        id='dropdown-country',
        options=[{'label': i, 'value': i} for i in unique_countries],
        value='None'
    ),
    html.H4('State'),
    html.Div(id='state_value'),
    dcc.Dropdown(id = 'dropdown-state',
        options = [{'label':'None', 'value':'None'}],
        value = 'None'
    ),
    html.H4('Length of Prediction'),
    html.Div('prediction-window'),
    dcc.Dropdown(id='dropdown-prediction-window',
        options = [{'label':f'{i} days','value':i} for i in [30,60,90]],
        value = 30),
    html.H4('Prediction'),
    html.Div(id='prediction')
])

#set state options according to chosen country
@app.callback(dash.dependencies.Output('dropdown-state', 'options'),
              [dash.dependencies.Input('dropdown-country', 'value')])
def add_states(country_value, df=full_df):
    country_df = full_df.loc[full_df['CountryName'] == country_value]
    state_df = country_df.loc[country_df['Jurisdiction'] 
                                == 'STATE_TOTAL'].dropna()
    global country
    country = country_value
    if len(state_df) > 0:
        return  [{'label':'None','value':'None'}] + [{'label':i,'value':i} \
            for i in state_df['RegionName'].dropna().unique()]
    else:
        return [{'label':'None', 'value':'None'}]

#reset state value
@app.callback(dash.dependencies.Output('dropdown-state','value'),
            [dash.dependencies.Input('dropdown-state','options')])
def reset_state_value(state_options):
    if state_options == [{'label':'None', 'value':'None'}]:
        return 'None'

#create prediction graph
@app.callback(dash.dependencies.Output('prediction', 'children'),
            [dash.dependencies.Input('dropdown-state','value'),
            dash.dependencies.Input('dropdown-country','value'),
            dash.dependencies.Input('dropdown-prediction-window','value'),
            dash.dependencies.Input('dropdown-prediction','value')])
def display_value(state, country, window, prediction, df=full_df):
    if country != 'None':
        return dcc.Graph(id='prediction-graph',
                    figure = graph_prediction(df, state=state,
                                              country=country,
                                              window=window,
                                              prediction=prediction))

if __name__ == '__main__':
    app.run_server(debug=True)