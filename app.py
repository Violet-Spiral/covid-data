import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objects as go
import pandas as pd
from src import *

# get data
full_df = get_covid_data()
unique_countries = sorted(full_df['CountryName'].unique())

# set initial app settings
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# display layout and components
app.layout = html.Div([
    html.H2('COVID-19 Cumulative Deaths or Positive Cases'),
    html.H4('To Display'),
    html.Div(id='stat-value'),
    dcc.Dropdown(
        id='dropdown-stat',
        options=[{'label':i,'value':i} for i in ['Cumulative Cases','Cumulative Deaths']]
    ),
    html.H4('Country'),
    html.Div(id='country-value'),
    dcc.Dropdown(
        id='dropdown-country',
        options=[{'label': i, 'value': i} for i in unique_countries],
        value='None'
    ),
    html.H4('State'),
    html.Div(id='state-value'),
    dcc.Dropdown(id = 'dropdown-state',
        options = [{'label':'None', 'value':'None'}],
        value = 'None'
    ),
    html.H4('Graph'),
    html.Div(id='graph')
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
            for i in sorted(state_df['RegionName'].dropna().unique())]
    else:
        return [{'label':'None', 'value':'None'}]

#reset state value
@app.callback(dash.dependencies.Output('dropdown-state', 'value'),
              [dash.dependencies.Input('dropdown-country', 'value')])
def reset_states(country_value, df=full_df):
    return 'None'

#create graph
@app.callback(dash.dependencies.Output('graph', 'children'),
            [dash.dependencies.Input('dropdown-state','value'),
            dash.dependencies.Input('dropdown-country','value'),
            dash.dependencies.Input('dropdown-stat','value')])
def display_value(state, country, stat, df=full_df):
    if country != 'None':
        return dcc.Graph(id='stat-graph',
                    figure = graph_stat(df, state=state,
                                              country=country,
                                              stat=stat))

if __name__ == '__main__':
    app.run_server(debug=True)