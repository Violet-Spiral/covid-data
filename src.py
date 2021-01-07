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
    return full_df

def get_prediction(df, window):
    """
    Helper function for graph_prediction to create, train, and create a prediction from a SARIMA model
    """
    cbrt_df = cbrt(df)
    model = SARIMAX(cbrt_df, order = (0,2,0), seasonal_order = (3,2,1,7), max_iter=200,
                                        freq = 'D')
    fit_model = model.fit(max_iter = 5, disp = False)
    yhat = fit_model.forecast(window)**3
    return yhat

def get_graph(df, yhat, state, country, window, prediction):
    """
    Helper function for graph_prediction to create and return plotly figure of prediction.
    """
    pred_start = yhat.index.date.min()
    pred_end = yhat.index.date.max()
    true_start = df.index.date.min()
    true_end = df.index.date.max()

    if state != 'None':
        title = f'{window} Day Forecast of Cumulative COVID-19 {prediction} in {state}, {country}'
    else:
        title = f'{window} Day Forecast of Cumulative COVID-19 {prediction} in {country}'
    fig = go.Figure(
                    data=[go.Scatter(x=df.index, y=df[prediction],
                                    name = 'Historical Cases')],
                    layout_title_text = title,
                    )
    fig.add_trace(go.Scatter(x=yhat.index, y=yhat.values,
                            name='Predicted Cases'))
    return fig

def graph_prediction(full_df, country='United States',
                    state=None, prediction='ConfirmedCases', window=30):
    """
    graph_prediction(full_df, country='United States',
                    state=None, prediction='ConfirmedCases', window=30)
    ---
    full_df should be a Pandas DataFrame with a time series index.  
    Function subsets full_df in respect to state and/or country. 
    Uses a SARIMA model to predict future COVID cases or deaths a number of days in the future defined by 'window'.  
    Returns a plotly figure of this prediction
    """
    if prediction not in ['ConfirmedCases','ConfirmedDeaths']:
        prediction = 'ConfirmedCases'

    if state in full_df['RegionName'].dropna().unique():
        df = full_df[(full_df['Jurisdiction'] == 'STATE_TOTAL') 
                    & (full_df['RegionName'] == state)][:-1]
    else: 
        df = full_df[(full_df['Jurisdiction'] == 'NAT_TOTAL') 
                    & (full_df['CountryName'] == country)][:-1]

    df.index.freq = 'D'
    df = df[[prediction]]
    df = df.interpolate(method='time', limit_direction='forward', 
                        limit_area='inside', downcast='infer')
    df = df[df[prediction] > 0]
    
    yhat = get_prediction(df, window)
    fig = get_graph(df, yhat, state, country, window, prediction)

    return fig