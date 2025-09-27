import dash
from dash import html, dcc, Input, Output, State, ctx
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ✅ Make sure you have the updated function in fetch_data.py
# (The one that returns a dictionary with all weather info)
from data.fetch_data import get_real_time_weather_data

dash.register_page(__name__, path='/seasonal', name='Seasonal Variations')

# Function to determine the season based on latitude and month
def get_season(latitude, month):
    """
    Determines the season based on latitude and month.
    Assumes a simplified model for Northern and Southern Hemispheres.
    """
    # Northern Hemisphere (latitude > 0)
    if latitude > 0:
        if 3 <= month <= 5:
            return "Spring"
        elif 6 <= month <= 8:
            # Adding 'Monsoon' for Indian context
            return "Summer / Monsoon"
        elif 9 <= month <= 11:
            return "Autumn"
        else: # 12, 1, 2
            return "Winter"
    # Southern Hemisphere (latitude < 0)
    elif latitude < 0:
        if 3 <= month <= 5:
            return "Autumn"
        elif 6 <= month <= 8:
            return "Winter"
        elif 9 <= month <= 11:
            return "Spring"
        else: # 12, 1, 2
            return "Summer"
    else: # Near Equator
        return "Tropical"

# Layout
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.H1("Seasonal Variations", className="page-title"),
        html.P("Observe how seasons are shifting by looking at long-term trends.", className="info-text"),
        dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True),

        # ✅ NEW: Live City Seasonal & Weather Info
        html.Div([
            html.H3("Live City Seasonal & Weather Info", className="live-data-title"),
            html.P("Enter a city to see live weather and its current season.", className="live-data-subtitle"),
            html.Div([
                dcc.Input(
                    id="live-city-input-seasonal",
                    type="text",
                    placeholder="Enter city...",
                    className="input-style"
                ),
                html.Button("Get Info", id="fetch-live-data-btn-seasonal", className="action-button"),
            ], className="input-group"),
            dcc.Loading(
                id="loading-live-seasonal",
                type="circle",
                children=html.Div(id="live-seasonal-output", className="api-output-box")
            ),
        ], className="live-data-container"),

        html.Hr(className="divider"),
        
        # Static section for future use (e.g., historical graph)
        html.Div([
            html.H3("Long-Term Seasonal Trends", className="live-data-title"),
            html.P("This section will display charts showing long-term seasonal trends from historical data.", className="api-info"),
            # Placeholder for a future graph
            dcc.Graph(id="seasonal-graph-placeholder", figure=go.Figure())
        ], className="live-data-container")

    ], className="info-container")
], className="main-wrapper")


# ✅ NEW: Callback to get and display live weather and season
@dash.callback(
    Output("live-seasonal-output", "children"),
    Input("fetch-live-data-btn-seasonal", "n_clicks"),
    State("live-city-input-seasonal", "value"),
    prevent_initial_call=True
)
def fetch_live_seasonal_info(n_clicks, city):
    if not city:
        return html.Div("Please enter a city name.", className="api-info")

    weather_data = get_real_time_weather_data(city)

    if "error" in weather_data:
        return html.Div(weather_data["error"], className="api-error")
    else:
        # Determine the current season
        today = datetime.now()
        current_month = today.month
        current_latitude = weather_data.get("lat")
        
        season = get_season(current_latitude, current_month)

        # Format the output
        city_name = weather_data.get("city", "N/A")
        temp = weather_data.get("temp_celsius", "N/A")
        humidity = weather_data.get("humidity_percent", "N/A")
        wind_speed_kmh = weather_data.get("wind_speed_kmh", "N/A")
        
        return html.Div([
            html.P(f"Current Season in {city_name}: ", className="live-season-title"),
            html.H4(f"{season}", className="live-season-output"),
            html.Hr(),
            html.P(f"Live Temperature: {temp}°C"),
            html.P(f"Live Humidity: {humidity}%"),
            html.P(f"Live Wind Speed: {wind_speed_kmh} km/h"),
        ], className="api-success")