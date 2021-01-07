import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from numpy import cbrt
from plotly import graph_objects as go

def get_covid_data():
    """
    Download latest covid data.
    """
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
    new_cols = {'ConfirmedCases':'Cumulative Cases','ConfirmedDeaths':'Cumulative Deaths'}
    full_df = full_df.rename(columns = new_cols)
    return full_df

def get_graph(df, state, country, stats):
    """
    get_graph(df, state, country, stats)
    ---
    Helper function for graph_stat to create and return plotly figure of chosen statistics.
    ---
    """

    if state != 'None':
        title = f'Cumulative COVID-19 in {state}, {country}'
    else:
        title = f'Cumulative COVID-19 in {country}'
    
    fig = go.Figure(layout_title_text = title)
    for stat in stats:
        fig.add_trace(go.Scatter(x=df.index, y=df[stat], name=stat))
    fig.update_layout(showlegend=True)

    return fig

def graph_stat(full_df, country='United States',
                    state=None, stats=['Cumulative Cases']):
    """
    graph_stat(full_df, country='United States',
                    state=None, stat='Cumulative Cases')
    ---
    Graphs chosen statistic(s)
    full_df should be a Pandas DataFrame with a time series index.  
    Function subsets full_df in respect to state and/or country. 
    Uses a SARIMA model to graph up to date COVID cases or deaths.
    Returns a plotly figure of deaths or cases
    ---
    """
    if not stats:
        stats = ['Cumulative Cases']

    if state in full_df['RegionName'].dropna().unique():
        df = full_df[(full_df['Jurisdiction'] == 'STATE_TOTAL') 
                    & (full_df['RegionName'] == state)][:-1]
    else: 
        df = full_df[(full_df['Jurisdiction'] == 'NAT_TOTAL') 
                    & (full_df['CountryName'] == country)][:-1]

    df = df.interpolate(method='time', limit_direction='forward', 
                        limit_area='inside', downcast='infer')
    df['Daily Cases'] = df['Cumulative Cases'].diff()
    df['Daily Deaths'] = df['Cumulative Deaths'].diff()
    df = df[stats]

    df = df.dropna()
    
    fig = get_graph(df, state, country, stats)

    return fig