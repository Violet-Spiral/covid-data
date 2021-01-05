import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

DATA_URL = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'
full_df = pd.read_csv(DATA_URL,
                      parse_dates=['Date'],
                      encoding="ISO-8859-1",
                      dtype={"RegionName": str,
                             "RegionCode": str,
                             "CountryName": str,
                             "CountryCode": str},
                      error_bad_lines=False)
unique_countries = full_df['CountryName'].unique()

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
    html.Div(id='state_value')
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
