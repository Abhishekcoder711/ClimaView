import copy
import math
import dash
from dash import html, dcc, Input, Output, State, ctx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ✅ Make sure you have the updated function in fetch_data.py
# (The one that returns a dictionary with all weather info)
from data.fetch_data import get_real_time_weather_data

dash.register_page(__name__, path='/wind', name='Wind Speed Analysis')

# Changed: include wind direction (degrees, 0 = north, 90 = east, etc.)
_state_wind_list = [
    {"state": "Andhra Pradesh", "lat": 16.51, "lon": 80.62, "wind": 3.5, "dir": 90},
    {"state": "Arunachal Pradesh", "lat": 27.09, "lon": 93.61, "wind": 2.8, "dir": 200},
    {"state": "Assam", "lat": 26.15, "lon": 91.77, "wind": 3.2, "dir": 180},
    {"state": "Bihar", "lat": 25.61, "lon": 85.13, "wind": 2.5, "dir": 160},
    {"state": "Chhattisgarh", "lat": 21.25, "lon": 81.63, "wind": 2.7, "dir": 140},
    {"state": "Goa", "lat": 15.49, "lon": 73.83, "wind": 4.1, "dir": 80},
    {"state": "Gujarat", "lat": 23.22, "lon": 72.65, "wind": 4.5, "dir": 70},
    {"state": "Haryana", "lat": 29.06, "lon": 76.08, "wind": 3.0, "dir": 120},
    {"state": "Himachal Pradesh", "lat": 31.10, "lon": 77.17, "wind": 2.3, "dir": 100},
    {"state": "Jharkhand", "lat": 23.34, "lon": 85.33, "wind": 2.6, "dir": 150},
    {"state": "Karnataka", "lat": 12.97, "lon": 77.59, "wind": 3.4, "dir": 90},
    {"state": "Kerala", "lat": 8.52, "lon": 76.92, "wind": 3.8, "dir": 85},
    {"state": "Madhya Pradesh", "lat": 23.25, "lon": 77.41, "wind": 2.9, "dir": 130},
    {"state": "Maharashtra", "lat": 19.07, "lon": 72.87, "wind": 3.9, "dir": 95},
    {"state": "Manipur", "lat": 24.82, "lon": 93.94, "wind": 2.7, "dir": 190},
    {"state": "Meghalaya", "lat": 25.57, "lon": 91.88, "wind": 2.6, "dir": 180},
    {"state": "Mizoram", "lat": 23.73, "lon": 92.72, "wind": 2.9, "dir": 200},
    {"state": "Nagaland", "lat": 25.67, "lon": 94.12, "wind": 2.8, "dir": 200},
    {"state": "Odisha", "lat": 20.27, "lon": 85.84, "wind": 3.1, "dir": 100},
    {"state": "Punjab", "lat": 30.74, "lon": 76.79, "wind": 3.2, "dir": 110},
    {"state": "Rajasthan", "lat": 26.91, "lon": 75.79, "wind": 4.0, "dir": 60},
    {"state": "Sikkim", "lat": 27.33, "lon": 88.61, "wind": 2.2, "dir": 190},
    {"state": "Tamil Nadu", "lat": 13.08, "lon": 80.27, "wind": 4.2, "dir": 80},
    {"state": "Telangana", "lat": 17.38, "lon": 78.48, "wind": 3.3, "dir": 95},
    {"state": "Tripura", "lat": 23.84, "lon": 91.28, "wind": 2.7, "dir": 180},
    {"state": "Uttar Pradesh", "lat": 26.85, "lon": 80.95, "wind": 2.8, "dir": 140},
    {"state": "Uttarakhand", "lat": 30.32, "lon": 78.03, "wind": 2.4, "dir": 120},
    {"state": "West Bengal", "lat": 22.57, "lon": 88.36, "wind": 3.0, "dir": 180},
    {"state": "Jammu & Kashmir", "lat": 34.08, "lon": 74.79, "wind": 2.5, "dir": 250},
    {"state": "Ladakh", "lat": 34.16, "lon": 77.58, "wind": 5.0, "dir": 270},
]

_df_wind_states = pd.DataFrame(_state_wind_list)

# Compute small vector endpoints for each state (convert km -> degrees approx)
# scale_km controls visual arrow length (tweak for readability)
scale_km_per_ms = 4.0  # multiplier to convert m/s to visible km length on the map
line_lats = []
line_lons = []
line_text = []

for _, r in _df_wind_states.iterrows():
    lat = r["lat"]
    lon = r["lon"]
    wind = r["wind"]
    bearing = r.get("dir", 0)
    theta = math.radians(bearing)  # bearing: 0 = north, increasing clockwise
    dist_km = wind * scale_km_per_ms
    # approximate degree offsets
    delta_lat = (dist_km * math.cos(theta)) / 111.0
    delta_lon = (dist_km * math.sin(theta)) / (111.0 * math.cos(math.radians(lat) + 1e-8))
    end_lat = lat + delta_lat
    end_lon = lon + delta_lon
    # append segment (use None to separate segments in one trace)
    line_lats += [lat, end_lat, None]
    line_lons += [lon, end_lon, None]
    line_text.append(f"{r['state']}: {wind} m/s, dir {bearing}°")

# Build mapbox figure with vector lines + markers
_mapbox_center = {"lat": 22.0, "lon": 82.0}
_fig_wind_base = go.Figure()

# line trace for wind vectors
_fig_wind_base.add_trace(
    go.Scattermapbox(
        lat=line_lats,
        lon=line_lons,
        mode="lines",
        line=dict(width=2, color="royalblue"),
        hoverinfo="none",
        name="Wind vectors",
    )
)

# marker trace for state points (sized & colored by wind speed)
_fig_wind_base.add_trace(
    go.Scattermapbox(
        lat=_df_wind_states["lat"],
        lon=_df_wind_states["lon"],
        mode="markers+text",
        text=_df_wind_states["state"],
        textposition="top center",
        marker=go.scattermapbox.Marker(
            size=_df_wind_states["wind"] * 6,  # visual scale
            color=_df_wind_states["wind"],
            colorscale="Blues",
            cmin=_df_wind_states["wind"].min(),
            cmax=_df_wind_states["wind"].max(),
            reversescale=False,
            opacity=0.9,
        ),
        hovertemplate="%{text}<br>Wind: %{marker.color} m/s<extra></extra>",
        name="States",
    )
)

_fig_wind_base.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=_mapbox_center,
        zoom=4,
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Average Wind Speed and Direction by State (sample, m/s)",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)

# Map component (mapbox)
india_wind_map = dcc.Graph(id="india-wind-map", figure=_fig_wind_base, config={"displayModeBar": True})

# Updated layout: include wind map, dropdown and details
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.H1("Wind Speed Analysis", className="page-title"),
        html.P("View current and past wind data to analyze patterns, storm strengths, and their impact on weather systems.", className="info-text"),
        dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True),

        # ✅ NEW: Live City Wind search box
        html.Div([
            html.H3("Live City Wind Speed", className="live-data-title"),
            html.P("Live wind speed and direction.", className="live-data-subtitle"),
            html.Div([
                dcc.Input(
                    id="live-city-input-wind",
                    type="text",
                    placeholder="Enter city...",
                    className="input-style"
                ),
                html.Button("Get Live Wind", id="fetch-live-data-btn-wind", className="action-button"),
            ], className="input-group"),
            dcc.Loading(
                id="loading-live-wind",
                type="circle",
                children=html.Div(id="live-wind-output", className="api-output-box")
            ),
        ], className="live-data-container"),

        html.Hr(className="divider"),
    ], className="info-container"),

    html.Div([html.H2("India — Statewise Wind Map (scatter_geo)"), india_wind_map], className="map-container"),
    html.Div([
        html.H2("State-wise Wind Details"),
        html.Div([
            html.Label("Search by state:"),
            dcc.Dropdown(
                id="wind-state-select",
                options=[{"label": s["state"], "value": s["state"]} for s in _state_wind_list],
                value=_state_wind_list[0]["state"],
                clearable=False,
                searchable=True,
                style={"width": "340px"},
            ),
            html.Div(id="wind-state-details", style={"marginTop": "12px"}),
        ], className="details-container"),
    ], className="details-section"),
], className="main-wrapper")

# Callback: re-center scatter_geo map to selected state by updating geo.center
@dash.callback(
    Output("india-wind-map", "figure"),
    Input("wind-state-select", "value"),
)
def _pan_to_wind_state(selected):
    row = _df_wind_states[_df_wind_states["state"] == selected]
    if row.empty:
        return _fig_wind_base
    lat = float(row["lat"].iloc[0])
    lon = float(row["lon"].iloc[0])
    fig = copy.deepcopy(_fig_wind_base)
    # update geo center
    fig.update_layout(mapbox_center={"lat": lat, "lon": lon}, mapbox=dict(center={"lat": lat, "lon": lon}, zoom=6))
    fig.update_traces(marker=dict(opacity=0.9))
    return fig

# Callback: show selected state's wind details
@dash.callback(Output("wind-state-details", "children"), Input("wind-state-select", "value"))
def _update_wind_state_details(selected_state):
    row = _df_wind_states[_df_wind_states["state"] == selected_state].squeeze()
    if row.empty:
        return html.Div("State not found")
    return html.Table([
        html.Tr([html.Th("State:"), html.Td(row["state"])]),
        html.Tr([html.Th("Avg wind speed (m/s):"), html.Td(float(row["wind"]))]),
        html.Tr([html.Th("Latitude:"), html.Td(row["lat"])]),
        html.Tr([html.Th("Longitude:"), html.Td(row["lon"])]),
    ], style={"border": "none", "marginTop": "6px"})

# ✅ NEW: Callback to get and display live wind data from API
@dash.callback(
    Output("live-wind-output", "children"),
    Input("fetch-live-data-btn-wind", "n_clicks"),
    State("live-city-input-wind", "value"),
    prevent_initial_call=True
)
def fetch_live_wind(n_clicks, city):
    if not city:
        return html.Div("Please enter a city name.", className="api-info")

    weather_data = get_real_time_weather_data(city)

    if "error" in weather_data:
        return html.Div(weather_data["error"], className="api-error")
    else:
        # OpenWeatherMap provides wind speed in m/s, let's also show km/h
        wind_speed_ms = weather_data.get("wind_speed_mps", "N/A")
        wind_speed_kmh = weather_data.get("wind_speed_kmh", "N/A")
        wind_direction = weather_data.get("wind_direction_deg", "N/A")

        output_text = f"Live wind speed in {weather_data['city']}: {wind_speed_ms} m/s ({wind_speed_kmh} km/h)"
        
        if wind_direction != "N/A":
            output_text += f" at {wind_direction}°"

        return html.Div(output_text, className="api-success")