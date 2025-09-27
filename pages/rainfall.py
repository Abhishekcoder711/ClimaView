import copy
import dash
from dash import html, dcc, Input, Output, State, ctx
import pandas as pd
import plotly.express as px

# ✅ Make sure you have the updated function in fetch_data.py
# (The one that returns a dictionary with all weather info)
from data.fetch_data import get_real_time_weather_data

dash.register_page(__name__, path="/rainfall", name="Rainfall Information")

# Sample state-centroid rainfall data (annual mm)
_state_list = [
    {"state": "Andhra Pradesh", "lat": 16.51, "lon": 80.62, "rainfall": 900},
    {"state": "Arunachal Pradesh", "lat": 27.09, "lon": 93.61, "rainfall": 2150},
    {"state": "Assam", "lat": 26.15, "lon": 91.77, "rainfall": 1800},
    {"state": "Bihar", "lat": 25.61, "lon": 85.13, "rainfall": 1200},
    {"state": "Chhattisgarh", "lat": 21.25, "lon": 81.63, "rainfall": 1300},
    {"state": "Goa", "lat": 15.49, "lon": 73.83, "rainfall": 3000},
    {"state": "Gujarat", "lat": 23.22, "lon": 72.65, "rainfall": 800},
    {"state": "Haryana", "lat": 29.06, "lon": 76.08, "rainfall": 620},
    {"state": "Himachal Pradesh", "lat": 31.10, "lon": 77.17, "rainfall": 1250},
    {"state": "Jharkhand", "lat": 23.34, "lon": 85.33, "rainfall": 1400},
    {"state": "Karnataka", "lat": 12.97, "lon": 77.59, "rainfall": 1200},
    {"state": "Kerala", "lat": 8.52, "lon": 76.92, "rainfall": 3000},
    {"state": "Madhya Pradesh", "lat": 23.25, "lon": 77.41, "rainfall": 1000},
    {"state": "Maharashtra", "lat": 19.07, "lon": 72.87, "rainfall": 1100},
    {"state": "Manipur", "lat": 24.82, "lon": 93.94, "rainfall": 1400},
    {"state": "Meghalaya", "lat": 25.57, "lon": 91.88, "rainfall": 2800},
    {"state": "Mizoram", "lat": 23.73, "lon": 92.72, "rainfall": 2500},
    {"state": "Nagaland", "lat": 25.67, "lon": 94.12, "rainfall": 1600},
    {"state": "Odisha", "lat": 20.27, "lon": 85.84, "rainfall": 1450},
    {"state": "Punjab", "lat": 30.74, "lon": 76.79, "rainfall": 600},
    {"state": "Rajasthan", "lat": 26.91, "lon": 75.79, "rainfall": 500},
    {"state": "Sikkim", "lat": 27.33, "lon": 88.61, "rainfall": 2800},
    {"state": "Tamil Nadu", "lat": 13.08, "lon": 80.27, "rainfall": 900},
    {"state": "Telangana", "lat": 17.38, "lon": 78.48, "rainfall": 900},
    {"state": "Tripura", "lat": 23.84, "lon": 91.28, "rainfall": 2000},
    {"state": "Uttar Pradesh", "lat": 26.85, "lon": 80.95, "rainfall": 1000},
    {"state": "Uttarakhand", "lat": 30.32, "lon": 78.03, "rainfall": 1500},
    {"state": "West Bengal", "lat": 22.57, "lon": 88.36, "rainfall": 1600},
    {"state": "Jammu & Kashmir", "lat": 34.08, "lon": 74.79, "rainfall": 800},
    {"state": "Ladakh", "lat": 34.16, "lon": 77.58, "rainfall": 100},
]

_df_states = pd.DataFrame(_state_list)

# Build initial Plotly mapbox figure (uses open-street-map style; no token required)
_fig_base = px.scatter_mapbox(
    _df_states,
    lat="lat",
    lon="lon",
    hover_name="state",
    hover_data={"rainfall": True, "lat": False, "lon": False},
    size="rainfall",
    color="rainfall",
    color_continuous_scale="Viridis",
    size_max=30,
    zoom=4,
    center={"lat": 22.0, "lon": 82.0},
)
_fig_base.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Average Annual Rainfall by State (sample, mm)",
)

# Map component (Plotly)
india_map = dcc.Graph(id="india-rainfall-map", figure=_fig_base, config={"displayModeBar": True})

# Page layout
layout = html.Div(
    [
        html.Div(className="sky"),
        html.Div(
            [
                html.H1("Rainfall Information", className="page-title"),
                html.P("Explore rainfall data by Indian state. Click markers or select a state for details.", className="info-text"),
                dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True),

                # ✅ NEW: Live City Rainfall search box
                html.Div([
                    html.H3("Live City Rainfall", className="live-data-title"),
                    html.P("Recent rainfall in the last 1-3 hours.", className="live-data-subtitle"),
                    html.Div([
                        dcc.Input(
                            id="live-city-input-rainfall",
                            type="text",
                            placeholder="Enter city...",
                            className="input-style"
                        ),
                        html.Button("Get Live Rainfall", id="fetch-live-data-btn-rainfall", className="action-button"),
                    ], className="input-group"),
                    dcc.Loading(
                        id="loading-live-rainfall",
                        type="circle",
                        children=html.Div(id="live-rainfall-output", className="api-output-box")
                    ),
                ], className="live-data-container"),

                html.Hr(className="divider"),
            ],
            className="info-container",
        ),
        html.Div([html.H2("India — Statewise Rainfall Map"), india_map], className="map-container"),
        html.Div(
            [
                html.H2("State-wise Rainfall Details"),
                html.Div(
                    [
                        html.Label("Search by state/country:"),
                        dcc.Dropdown(
                            id="state-select",
                            options=[{"label": s["state"], "value": s["state"]} for s in _state_list],
                            value=_state_list[0]["state"],
                            clearable=False,
                            searchable=True,
                            style={"width": "340px"},
                        ),
                        html.Div(id="state-details", style={"marginTop": "12px"}),
                    ],
                    className="details-container",
                ),
            ],
            className="details-section",
        ),
    ],
    className="main-wrapper",
)

# Callback: pan/zoom map to selected state by updating the figure center and zoom
@dash.callback(
    Output("india-rainfall-map", "figure"),
    Input("state-select", "value"),
)
def _pan_to_state(selected):
    row = _df_states[_df_states["state"] == selected]
    if row.empty:
        return _fig_base
    lat = float(row["lat"].iloc[0])
    lon = float(row["lon"].iloc[0])
    # create a deep copy of base figure and adjust center + zoom
    fig = copy.deepcopy(_fig_base)
    fig.update_layout(mapbox_center={"lat": lat, "lon": lon}, mapbox=dict(center={"lat": lat, "lon": lon}, zoom=6))
    # ensure hover highlights selected point more clearly
    fig.update_traces(marker=dict(opacity=0.9))
    return fig

# Callback: show selected state details (always registered)
@dash.callback(Output("state-details", "children"), Input("state-select", "value"))
def _update_state_details(selected_state):
    row = _df_states[_df_states["state"] == selected_state].squeeze()
    if row.empty:
        return html.Div("State not found")
    return html.Table(
        [
            html.Tr([html.Th("State:"), html.Td(row["state"])]),
            html.Tr([html.Th("Avg annual rainfall (mm):"), html.Td(int(row["rainfall"]))]),
            html.Tr([html.Th("Latitude:"), html.Td(row["lat"])]),
            html.Tr([html.Th("Longitude:"), html.Td(row["lon"])]),
        ],
        style={"border": "none", "marginTop": "6px"},
    )

# ✅ NEW: Callback to get and display live rainfall from API
@dash.callback(
    Output("live-rainfall-output", "children"),
    Input("fetch-live-data-btn-rainfall", "n_clicks"),
    State("live-city-input-rainfall", "value"),
    prevent_initial_call=True
)
def fetch_live_rainfall(n_clicks, city):
    if not city:
        return html.Div("Please enter a city name.", className="api-info")

    weather_data = get_real_time_weather_data(city)

    if "error" in weather_data:
        return html.Div(weather_data["error"], className="api-error")
    else:
        # OpenWeatherMap returns rainfall data under a 'rain' key
        # Check for both 1h and 3h rainfall data
        rain_info = "No recent rainfall data available."
        
        if "rain" in weather_data:
            if "1h" in weather_data["rain"]:
                rain_amount = weather_data["rain"]["1h"]
                rain_info = f"Rainfall in last 1 hour: {rain_amount} mm"
            elif "3h" in weather_data["rain"]:
                rain_amount = weather_data["rain"]["3h"]
                rain_info = f"Rainfall in last 3 hours: {rain_amount} mm"

        return html.Div(f"Live rainfall info for {weather_data['city']}: {rain_info}", className="api-success")