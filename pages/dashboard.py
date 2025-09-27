from dash import html, dcc, Input, Output, State, ctx, no_update, dash_table, callback
import pandas as pd
import plotly.express as px
import datetime
import os
from dotenv import load_dotenv
from data.fetch_data import get_real_time_temperature
import dash_bootstrap_components as dbc
import random
import dash

# Register page
dash.register_page(__name__, path="/dashboard")

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Load climate data
df = pd.read_csv("data/climate.csv")
df["Year"] = df["Year"].astype(int)
ranked_df = df.copy()
ranked_df["Rank"] = ranked_df.groupby("Year")["Temperature"].rank(ascending=False)

# AI Tips
ai_tips = [
    "💡 Reduce, Reuse, Recycle!",
    "🌱 Plant trees to absorb CO₂.",
    "💧 Save water! Every drop counts for the planet.",
    "🚲 Use public transport or cycle to reduce emissions.",
    "🔌 Turn off electronics when not in use.",
    "🌍 Support clean energy sources."
]

# English language support
languages = {
    "EN": {
        "title": "ClimaView",
        "select_year": "📅 Select Year:",
        "select_country": "Select Country:",
        "live_temp": "City Temperature:",
        "get_temp": "Get Temperature",
        "download": "Download Map",
        "ai_tips": "Climate Awareness Tips!!"
    }
}

min_year = df["Year"].min()
max_year = df["Year"].max()
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Delhi")

# Layout of the dashboard
layout = html.Div([
    dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    dcc.Store(id='city-store', data={'city': DEFAULT_CITY}),
    dcc.Store(id='initial-load-trigger', data=0),

    # HAMBURGER + SIDEBAR WRAPPER
    html.Div([
        # Hamburger button
        html.Button("☰", id="menu-btn", className="menu-icon"),

        # LEFT SIDEBAR
        html.Div([
            # 'Download Map' button ko yahan se hata diya gaya hai
            html.Hr(),
        ], className="sidebar-panel", id="sidebar-panel", style={"display": "none", "height": "900vh"}),
    ]),

    # MAIN CONTENT
    html.Div([
        html.Div([
            html.Div([
                html.H1(id="app-title", className="app-title", children=languages["EN"]["title"])
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),

            html.Div(id="live-datetime", style={"fontSize": "13px", "marginTop": "8px"}),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),

        # New City Temperature Section
        html.Div([
            html.Div([
                dcc.Input(id="city-input", type="text", placeholder="Enter city....", className="input", style={"width": "30%", "marginRight": "10px"}, value=DEFAULT_CITY),
                html.Button(id="api-button", className="action-button", children=languages["EN"]["get_temp"]),
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
            html.Div(id="api-output", className="temperature-output-box", style={"marginTop": "10px"})
        ], className="city-temperature-section", style={"marginBottom": "20px"}),

        # Download button ko yahan se hata diya gaya hai
        # dcc.Download(id="download-image"),

        html.Div([
            html.H3("India's Climate Insights", style={"fontSize":"30px", "marginTop": "50px", "marginBottom": "20px", "color": "white"}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-cloud-rain", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Rainfall Information", style={"marginBottom": "5px"}),
                    html.P("Explore rainfall data", style={"fontSize": "12px"}),
                    html.A("Explore Now", href="/rainfall", style={"fontSize": "12px"})
                ], className="service-block"),
                html.Div([
                    html.I(className="fas fa-sun", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Temperature Trends", style={"marginBottom": "5px"}),
                    html.P("Analyze long-term temperature shifts", style={"fontSize": "12px"}),
                    html.A("Learn More", href="/temperature", style={"fontSize": "12px"})
                ], className="service-block"),
                html.Div([
                    html.I(className="fas fa-wind", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Wind Speed Analysis", style={"marginBottom": "5px"}),
                    html.P("View current and past wind data", style={"fontSize": "12px"}),
                    html.A("See Details", href="/wind", style={"fontSize": "12px"})
                ], className="service-block"),
            ], className="services-row", style={"marginBottom": "0px"}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-tint", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Humidity Levels", style={"marginBottom": "5px"}),
                    html.P("Track changes in atmospheric moisture", style={"fontSize": "12px"}),
                    html.A("View Data", href="/humidity", style={"fontSize": "12px"})
                ], className="service-block"),
                html.Div([
                    html.I(className="fas fa-thermometer-half", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Seasonal Variations", style={"marginBottom": "5px"}),
                    html.P("Observe temperature patterns across seasons", style={"fontSize": "12px"}),
                    html.A("Discover Trends", href="/seasonal", style={"fontSize": "12px"})
                ], className="service-block"),
                html.Div([
                    html.I(className="fas fa-chart-line", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Climate Projections", style={"marginBottom": "5px"}),
                    html.P("Explore future climate scenarios", style={"fontSize": "12px"}),
                    html.A("View Forecasts", href="projections", style={"fontSize": "12px"})
                ], className="service-block"),
            ], className="services-row"),
        ], className="our-climate-insights", style={"marginBottom": "20px"}),
        
        # New Global Climate Metrics Section with only one service block and a Data Table service block
        html.Div([
            html.H3("Global Climate Metrics", style={"fontSize":"30px", "marginTop": "50px", "marginBottom": "20px", "color": "white"}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-globe-americas", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("World Insights", style={"marginBottom": "5px"}),
                    html.P("Analyze climate trends across the globe.", style={"fontSize": "12px"}),
                    html.A("View Trends", href="/global-metrics", style={"fontSize": "12px"})
                ], className="service-block"),
                # New Data Table service box
                html.Div([
                    html.I(className="fas fa-table", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Data Table", style={"marginBottom": "5px"}),
                    html.P("View and filter historical global climate data.", style={"fontSize": "12px"}),
                    html.A("Explore Data", href="/data-table", style={"fontSize": "12px"})
                ], className="service-block"),
                html.Div([
                    html.I(className="fas fa-sea", style={"fontSize": "24px", "marginBottom": "5px"}),
                    html.H4("Sea Lavel", style={"marginBottom": "5px"}),
                    html.P("Analyze the sea label across globe", style={"fontSize": "12px"}),
                    html.A("Explore Data", href="/sea-lavel", style={"fontSize": "12px"})
                ], className="service-block"),
            ], className="services-row", style={"marginBottom": "20px"}),
        ], className="our-climate-insights", style={"marginBottom": "20px"}),


        html.Div([
            html.H2(id="ai-tips-title", children=languages["EN"]["ai_tips"]),
            html.Div(id="ai-tip-box")
        ], className="ai-tips-sidebar"),
    ], className="main-content")
], style={"display": "flex"})

# Callback to set default city value
@callback(
    Output("city-input", "value"),
    Input("city-store", "data")
)
def set_default_city(data):
    return data['city'] if data and 'city' in data else DEFAULT_CITY

# Toggle sidebar
@callback(
    Output("sidebar-panel", "style"),
    Input("menu-btn", "n_clicks"),
    State("sidebar-panel", "style"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, current_style):
    if current_style and current_style.get("display") == "block":
        return {"display": "none"}
    else:
        return {"display": "block"}

# API Temp
@callback(
    Output("api-output", "children"),
    Input("api-button", "n_clicks"),
    Input('initial-load-trigger', 'data'),
    State("city-input", "value"),
    prevent_initial_call=False
)
def fetch_temp(n_clicks, initial_load_data, city):
    # This check ensures the callback only runs when the button is clicked or on initial load
    if not ctx.triggered or ctx.triggered[0]['prop_id'] in ['api-button.n_clicks', 'initial-load-trigger.data']:
        if not city:
            return "Please enter a city name."

        temp = get_real_time_temperature(city)
        return f"Real-time temperature in {city}: {temp}°C" if isinstance(temp, (int, float)) else temp
    
    return no_update

# AI Tip
@callback(
    Output("ai-tip-box", "children"),
    Input("interval-clock", "n_intervals")
)
def update_ai_tips(n):
    return random.choice(ai_tips)