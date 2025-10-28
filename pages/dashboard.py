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

dash.register_page(__name__, path="/dashboard")

# Load climate data
try:
    # NOTE: Ensure 'data/climate.csv' exists in your project structure
    df = pd.read_csv("data/climate.csv")
    df["Year"] = df["Year"].astype(int)
    ranked_df = df.copy()
    ranked_df["Rank"] = ranked_df.groupby("Year")["Temperature"].rank(ascending=False)
    min_year = df["Year"].min()
    max_year = df["Year"].max()
except FileNotFoundError:
    print("Warning: climate.csv not found. Using dummy data for min/max year.")
    min_year = 2000
    max_year = 2024
    df = pd.DataFrame()
    ranked_df = pd.DataFrame()


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

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Delhi")

# --- NEWS SECTION HELPER FUNCTION ---
def get_weather_news():
    # Dummy function as I don't have the news_module
    return [
        {'title': 'Global Temperatures Hit Record Highs in 2024', 'url': '#', 'source': 'WMO'},
        {'title': 'Monsoon Forecast: Above Average Rainfall Predicted', 'url': '#', 'source': 'IMD'},
        {'title': 'New Study on Sea Level Rise Impacts Coastal Cities', 'url': '#', 'source': 'NASA'}
    ]

def create_news_section_layout():
    """Generates the Dash layout for the weather news feed."""
    news_data = get_weather_news()
    
    # Error Handling UI
    if not news_data:
        return html.Div(
            [html.P("Weather News currently unavailable. Check API key or internet connection.")], 
            className="api-info news-section-card"
        )
        
    news_items = []
    for item in news_data:
        news_items.append(
            html.Div([
                html.A(
                    item['title'], 
                    href=item['url'], 
                    target="_blank", 
                    className="news-link"
                ),
                html.P(f"Source: {item['source']}", className="news-source")
            ], className="news-item-card")
        )

    return html.Div(
        [
            html.H2("Global Weather News Feed", className="news-heading"),
            html.Div(news_items, className="news-list-container")
        ],
        className="news-section-card"
    )
# --------------------------------------

# --- NEW FOOTER HELPER FUNCTION ---
def create_footer_layout(languages_data):
    """Generates the Dash layout for the footer section with About Us, Contact, and Copyright."""
    current_year = datetime.datetime.now().year
    
    return html.Div([
        html.Div([
            html.A("About Us", href="/about", className="footer-link"),
            html.Span("|", className="footer-separator"),
            html.A("Contact", href="/contact", className="footer-link"),
            html.Span("|", className="footer-separator"),
            html.A("Privacy Policy", href="/privacy", className="footer-link"),
        ], className="footer-links-container"),
        
        # NOTE: Font Awesome or similar library is required for these icons to display
        html.Div([
            html.A(html.I(className="fab fa-facebook-f"), href="#", target="_blank", className="social-icon"),
            html.A(html.I(className="fab fa-twitter"), href="#", target="_blank", className="social-icon"),
            html.A(html.I(className="fab fa-linkedin-in"), href="#", target="_blank", className="social-icon"),
        ], className="footer-social-container"),
        
        html.P(
            f"© Copyright {current_year} {languages_data['EN']['title']}. All rights reserved.", 
            className="copyright-text"
        )
    ], className="footer-section")
# --------------------------------------


# Layout of the dashboard
layout = html.Div([
    dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    dcc.Store(id='city-store', data={'city': DEFAULT_CITY}),
    dcc.Store(id='initial-load-trigger', data=0),

    # --- TOP NAVIGATION BAR (NAVBAR) ---
    html.Nav([
        # Left side: ClimaView (Home Link) and Live Time
        html.Div([
            html.A(
                html.H1(id="app-title-nav", className="app-title-nav", children=languages["EN"]["title"]), 
                className="navbar-brand"
            ),
            html.Div(id="live-datetime-nav", className="live-datetime-nav")
        ], className="navbar-left"),

        # Right side: Navigation Links
        html.Div([
            dcc.Link("Home", href="/", className="nav-link"),
            dcc.Link("Rainfall Info", href="/rainfall", className="nav-link"),
            dcc.Link("Temperature", href="/temperature", className="nav-link"),
            dcc.Link("Humidity", href="/humidity", className="nav-link"),
            dcc.Link("Wind Pressure", href="/wind", className="nav-link"),
            dcc.Link("Sea Level", href="/sea-level", className="nav-link"),
        ], className="navbar-right"),
    ], className="top-navbar"),
    # ----------------------------------------

    # HAMBURGER + SIDEBAR WRAPPER 
    html.Div([
        # Hamburger button (Fixed Position in CSS)
        html.Button("☰", id="menu-btn", className="menu-icon")
        ,

        # LEFT SIDEBAR - Initial state is hidden via CSS transform
        html.Div([
            # Sidebar Content goes here
            html.H4("Controls", style={"marginTop": "0"}),
            html.Hr(),
            html.P(languages["EN"]["select_year"]),
            dcc.RangeSlider(
                id="year-slider",
                min=min_year,
                max=max_year,
                step=1,
                value=[min_year, max_year],
                marks={str(year): str(year) for year in range(min_year, max_year + 1, 10)},
                tooltip={"placement": "bottom", "always_visible": False},
                className="range-slider"
            ),
            html.Br(),
            html.Button(languages["EN"]["download"], id="download-map-btn", className="action-button sidebar-btn"),
            html.Hr(),
            # You can add other controls/links here
            dcc.Link("Data Table View", href="/data-table", className="nav-link sidebar-link"),
        ], className="sidebar-panel", id="sidebar-panel"), 
    ], className="menu-wrapper"),

    # MAIN CONTENT 
    html.Div([
        # New City Temperature Section (Existing)
        html.Div([
            html.Div([
                dcc.Input(id="city-input", type="text", placeholder="Enter city....", className="input", style={"width": "30%", "marginRight": "10px"}, value=DEFAULT_CITY),
                html.Button(id="api-button", className="action-button", children=languages["EN"]["get_temp"]),
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
            html.Div(id="api-output", className="temperature-output-box", style={"marginTop": "10px"})
        ], className="city-temperature-section", style={"marginBottom": "20px"}),

        # India's Climate Insights Section (Existing)
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
        
        # Global Climate Metrics Section (Existing)
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
                    html.I(className="fas fa-water", style={"fontSize": "24px", "marginBottom": "5px"}), 
                    html.H4("Sea Level", style={"marginBottom": "5px"}),
                    html.P("Analyze the sea level across globe", style={"fontSize": "12px"}),
                    html.A("Explore Data", href="/sea-level", style={"fontSize": "12px"})
                ], className="service-block"),
            ], className="services-row", style={"marginBottom": "20px"}),
        ], className="our-climate-insights", style={"marginBottom": "20px"}),

        # News Section (Existing)
        create_news_section_layout(),
        
        html.Div([
            html.H2(id="ai-tips-title", children=languages["EN"]["ai_tips"]),
            html.Div(id="ai-tip-box")
        ], className="ai-tips-sidebar"),
    ], className="main-content", id="main-content"),

    # --- FOOTER SECTION (NEWLY ADDED) ---
    create_footer_layout(languages) 
    # -------------------------------------

], style={"display": "flex", "flexDirection": "column"})

# --- CALLBACKS ---

# Callback to set default city value (Existing)
@callback(
    Output("city-input", "value"),
    Input("city-store", "data")
)
def set_default_city(data):
    return data['city'] if data and 'city' in data else DEFAULT_CITY

# Toggle sidebar (Existing)
@callback(
    Output("sidebar-panel", "className"),
    Input("menu-btn", "n_clicks"),
    State("sidebar-panel", "className"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, current_sidebar_class):
    
    # Initialize class if it's None/missing
    if current_sidebar_class is None:
        current_sidebar_class = "sidebar-panel"
    
    is_open = "open" in current_sidebar_class.split()

    if is_open:
        # Hide Sidebar
        new_sidebar_class = current_sidebar_class.replace(" open", "").strip()
    else:
        # Show Sidebar
        if not current_sidebar_class.startswith("sidebar-panel"):
            new_sidebar_class = "sidebar-panel open"
        else:
             new_sidebar_class = current_sidebar_class + " open"

    return new_sidebar_class


# API Temp (Existing)
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

        try:
            # NOTE: This function MUST be correctly implemented in data/fetch_data.py
            temp = get_real_time_temperature(city)
            return f"Real-time temperature in {city}: {temp}°C" if isinstance(temp, (int, float)) else temp
        except Exception as e:
             # Basic error handling for API call failure
             return f"Error fetching temperature for {city}. Check API key or city name. (Error: {e})"

    return no_update

# Live Clock Callback (Existing)
@callback(
    Output("live-datetime-nav", "children"), 
    Input("interval-clock", "n_intervals")
)
def update_datetime(n):
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# AI Tip (Existing)
@callback(
    Output("ai-tip-box", "children"),
    Input("interval-clock", "n_intervals")
)

def update_ai_tips(n):
    # This interval runs every second, but you might want to change the tip less often.
    # For now, it changes on every interval run.
    return random.choice(ai_tips)