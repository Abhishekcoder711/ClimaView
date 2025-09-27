import dash
from dash import html, dcc, Input, Output, State, ctx
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ✅ Make sure you have the new function in fetch_data.py
from data.fetch_data import get_5_day_forecast_data

dash.register_page(__name__, path='/projections', name='Climate Projections')

# Page layout
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.H1("Climate Projections", className="page-title"),
        html.P("Explore future climate scenarios and forecasts based on scientific models and current data. Prepare for what's to come.", className="info-text"),
        dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True),

        # ✅ NEW: Live 5-Day Forecast Search Box
        html.Div([
            html.H3("Live 5-Day Weather Forecast", className="live-data-title"),
            html.P("Enter a city to see its short-term weather forecast.", className="live-data-subtitle"),
            html.Div([
                dcc.Input(
                    id="live-city-input-projections",
                    type="text",
                    placeholder="Enter city...",
                    className="input-style"
                ),
                html.Button("Get Forecast", id="fetch-forecast-btn", className="action-button"),
            ], className="input-group"),
            dcc.Loading(
                id="loading-forecast",
                type="circle",
                children=html.Div(id="live-forecast-output", className="api-output-box")
            ),
        ], className="live-data-container"),

        html.Hr(className="divider"),
        
        # Static section for long-term models
        html.Div([
            html.H3("Long-Term Climate Models", className="live-data-title"),
            html.P("This section will display charts from long-term climate projection models, which are based on historical data and not live APIs.", className="api-info"),
            # Placeholder for a future graph
            dcc.Graph(id="projection-graph-placeholder", figure=go.Figure())
        ], className="live-data-container")

    ], className="info-container")
], className="main-wrapper")


# ✅ NEW: Callback to fetch and display the 5-day forecast
@dash.callback(
    Output("live-forecast-output", "children"),
    Input("fetch-forecast-btn", "n_clicks"),
    State("live-city-input-projections", "value"),
    prevent_initial_call=True
)
def fetch_forecast(n_clicks, city):
    if not city:
        return html.Div("Please enter a city name.", className="api-info")

    forecast_data = get_5_day_forecast_data(city)

    if "error" in forecast_data:
        return html.Div(forecast_data["error"], className="api-error")
    else:
        forecast_list = forecast_data.get("forecast", [])
        city_name = forecast_data.get("city", "N/A")

        if not forecast_list:
            return html.Div(f"No forecast data available for {city_name}.", className="api-error")

        # Create forecast cards for each day
        forecast_cards = [
            html.Div([
                html.P(item["date"], className="forecast-date"),
                html.P(f"Temp: {item['temp_celsius']}°C"),
                html.P(f"Weather: {item['weather_desc']}"),
                html.P(f"Humidity: {item['humidity_percent']}%"),
                html.P(f"Wind: {item['wind_speed_kmh']} km/h"),
            ], className="forecast-card")
            for item in forecast_list
        ]
        
        return html.Div([
            html.H4(f"5-Day Forecast for {city_name}"),
            html.Div(forecast_cards, className="forecast-cards-container")
        ], className="api-success")