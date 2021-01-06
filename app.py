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
unique_states = []

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
unique_states = []

app.layout = html.Div([
    html.H2('COVID-19 Cumulative Infections Prediction'),
    html.H4('Country'),
    dcc.Dropdown(
        id='dropdown-country',
        options=[{'label': i, 'value': i} for i in unique_countries],
        value='None'
    ),
    html.H4('State'),
    html.Div(id='state_value'),
    dcc.Dropdown(id = 'dropdown-state',
        options = [{'label':'None Available', 'value':'None'}],
        value = 'Choose a State'
    ),
    html.H4('Length of Prediction'),
    html.Div('prediction-window'),
    dcc.Dropdown(id='dropdown-prediction-window',
        options = [{'label':f'{i} days','value':i} for i in [30,60,90]],
        value = 30),
    html.H4('Prediction'),
    html.Div(id='prediction')
])


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

@app.callback(dash.dependencies.Output('dropdown-state','value'),
            [dash.dependencies.Input('dropdown-state','options')])
def reset_state_value(state_options):
    if state_options == [{'label':'None', 'value':'None'}]:
        return None


@app.callback(dash.dependencies.Output('prediction', 'children'),
            [dash.dependencies.Input('dropdown-state','value'),
            dash.dependencies.Input('dropdown-country','value'),
            dash.dependencies.Input('dropdown-prediction-window','value')])
def display_value(state_value, country_value, window_value, df=full_df):
    if country_value != 'None':
        return dcc.Graph(id='prediction-graph',
                    figure = graph_prediction(full_df, state = state_value, \
                                              country = country_value,
                                              window=window_value)
                    )

# @app.callback(dash.dependencies.Output('state_value', 'children'),
#             [dash.dependencies.Input('dropdown_country', 'value')])
# def state_list(country):
#     return graph_prediction(full_df, country=country_value, state=state_value)

if __name__ == '__main__':
    app.run_server(debug=True)
