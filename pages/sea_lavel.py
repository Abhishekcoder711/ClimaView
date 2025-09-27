import dash
from dash import dcc, html, callback, Input, Output
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

# Register the page
dash.register_page(__name__, path='/sea-label', name='Sea Level')

# Load API key from environment variables
load_dotenv()
NOAA_API_KEY = os.getenv("NOAA_API_KEY")

# Layout for the Sea Level page
layout = html.Div([
    html.H1("Global Sea Level Trends", className="app-title"),
    html.Hr(style={"borderTop": "2px solid #bbb", "marginTop": "10px", "marginBottom": "20px"}),
    
    dcc.Link(html.Button("Go to Dashboard"), href="/dashboard", style={"marginTop": "20px", "backgroundColor": "#2C4057", "color": "white", "padding": "10px", "border": "none", "borderRadius": "10px", "cursor": "pointer"}),

    html.P("Analyze historical sea level data from NOAA.", style={"color": "white", "fontSize": "22px", "marginBottom": "20px", "marginTop": "20px"}),

    html.Div([
        html.Label("📅 Select Year (Data from NOAA):", style={"color": "white", "fontSize": "18px"}),
        dcc.Dropdown(
            id="sea-label-year-dropdown",
            options=[{"label": str(y), "value": str(y)} for y in range(2000, 2025)], # Year range, adjust as needed
            value='2014',
            style={'width': '120px'}
        ),
    ], style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "20px"}),

    dcc.Graph(id="sea-level-graph", style={"marginTop": "30px"}),
    html.Div(id="error-message", style={'color': 'red', 'marginTop': '10px'})

], className="main-content")

# Callback to update the graph based on the selected year
@callback(
    Output("sea-level-graph", "figure"),
    Output("error-message", "children"),
    Input("sea-label-year-dropdown", "value")
)
def update_sea_level_graph(selected_year):
    if not NOAA_API_KEY:
        return {}, "Error: NOAA API key is not set. Please add it to your .env file."

    # API request parameters
    start_date = f"{selected_year}0101"
    end_date = f"{selected_year}1231"
    
    # Ek bade station ka udaharan (apko apne project ke liye sahi station ID dhoondhni hogi)
    station_id = "8518750" # New York Station

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
    
    # API key ko headers mein daalein
    headers = {
        "token": NOAA_API_KEY
    }

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Check for empty data or API errors
        if 'error' in data:
            return {}, f"Error from API: {data['error']['message']}"
        if not 'data' in data or not data['data']:
            return {}, f"No data available for {selected_year} at this station. Try another year or a different station ID."

        df_raw = pd.DataFrame(data['data'])
        df_raw.rename(columns={'t': 'Date_Time', 'v': 'Water_Level'}, inplace=True)
        df_raw['Date_Time'] = pd.to_datetime(df_raw['Date_Time'])
        df_raw['Water_Level'] = pd.to_numeric(df_raw['Water_Level'])

        fig = px.line(df_raw, x="Date_Time", y="Water_Level", title=f"Mean Sea Level at {station_id} in {selected_year}")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            title_font=dict(size=24, color='white')
        )
        return fig, ""
    
    except requests.exceptions.RequestException as e:
        return {}, f"Failed to fetch data from NOAA: {e}"
    except Exception as e:
        return {}, f"An unexpected error occurred: {e}"