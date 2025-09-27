import requests
import pandas as pd
import os
from dotenv import load_dotenv

# .env file se API key load karein
load_dotenv()
NOAA_API_KEY = os.getenv("NOAA_API_KEY")

def fetch_sea_level_data(year, station_id="8518750"):
    """
    NOAA API se saal ke hisaab se samudra ke star ka data fetch karta hai.
    
    Args:
        year (str): Jis saal ka data chahiye.
        station_id (str): NOAA station ID. Default New York station.
        
    Returns:
        pd.DataFrame: Pandas DataFrame jisme samudra ke star ka data hota hai.
                      Agar error ho to None return karta hai.
    """
    if not NOAA_API_KEY:
        print("Error: NOAA API key is not set in the .env file.")
        return None

    # API request parameters
    start_date = f"{year}0101"
    end_date = f"{year}1231"
    
    api_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "begin_date": start_date,
        "end_date": end_date,
        "station": station_id,
        "product": "water_level",
        "datum": "MSL",
        "units": "metric",
        "time_zone": "gmt",
        "application": "Dash_App",
        "format": "json"
    }
    
    headers = {
        "token": NOAA_API_KEY
    }

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # HTTP errors ko catch karein
        data = response.json()

        if 'error' in data:
            print(f"Error from API: {data['error']['message']}")
            return None
        if not 'data' in data or not data['data']:
            print(f"No data available for {year} at station {station_id}.")
            return None

        df_raw = pd.DataFrame(data['data'])
        df_raw.rename(columns={'t': 'Date_Time', 'v': 'Water_Level'}, inplace=True)
        df_raw['Date_Time'] = pd.to_datetime(df_raw['Date_Time'])
        df_raw['Water_Level'] = pd.to_numeric(df_raw['Water_Level'])
        
        return df_raw
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Udaharan ke liye function ko test karein
if __name__ == "__main__":
    df_2023 = fetch_sea_level_data("2023")
    if df_2023 is not None:
        print(df_2023.head())