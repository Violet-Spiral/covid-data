def download_latest_covid_data():
    import pandas as pd
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
    full_df.to_csv('latest_covid_data.csv')
if __name__ == '__main__':
    download_latest_covid_data()