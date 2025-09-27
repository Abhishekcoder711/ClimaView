import dash
from dash import html, dcc, Input, Output, State, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import copy

# ✅ Make sure you have the updated function in fetch_data.py
# (The one that returns a dictionary with all weather info)
from data.fetch_data import get_real_time_weather_data

dash.register_page(__name__, path='/humidity', name='Humidity Levels')

# Sample state humidity dataset (state, humidity %, approximate centroid lat/lon)
_state_data = [
    {"state": "Punjab", "humidity": 68, "lat": 31.1471, "lon": 75.3412},
    {"state": "Haryana", "humidity": 64, "lat": 29.0588, "lon": 76.0856},
    {"state": "Delhi", "humidity": 70, "lat": 28.7041, "lon": 77.1025},
    {"state": "Himachal Pradesh", "humidity": 55, "lat": 31.1048, "lon": 77.1734},
    {"state": "Rajasthan", "humidity": 40, "lat": 27.0238, "lon": 74.2179},
    {"state": "Uttar Pradesh", "humidity": 60, "lat": 26.8467, "lon": 80.9462},
    {"state": "Maharashtra", "humidity": 58, "lat": 19.7515, "lon": 75.7139},
    {"state": "Karnataka", "humidity": 66, "lat": 15.3173, "lon": 75.7139},
    {"state": "Gujarat", "humidity": 52, "lat": 22.2587, "lon": 71.1924},
    {"state": "West Bengal", "humidity": 72, "lat": 22.9868, "lon": 87.8550},
    {"state": "Bihar", "humidity": 69, "lat": 25.0961, "lon": 85.3131},
]
_df_states = pd.DataFrame(_state_data)

# helper to build base figure showing all states
def _build_figure(selected_state=None):
    fig = px.scatter_mapbox(
        _df_states,
        lat="lat",
        lon="lon",
        hover_name="state",
        hover_data={"humidity": True, "lat": False, "lon": False},
        size="humidity",
        size_max=18,
        zoom=4,
        center={"lat": _df_states["lat"].mean(), "lon": _df_states["lon"].mean()},
        mapbox_style="open-street-map",
    )
    # reduce marker opacity for better visibility
    fig.update_traces(marker=dict(opacity=0.7, sizemode="area", color="royalblue"))

    # if a specific state is selected, add a highlighted trace and center the map
    if selected_state and selected_state != "All":
        sel = _df_states[_df_states["state"] == selected_state]
        if not sel.empty:
            lat = float(sel["lat"].iloc[0])
            lon = float(sel["lon"].iloc[0])
            humidity = sel["humidity"].iloc[0]
            fig.add_trace(
                go.Scattermapbox(
                    lat=[lat],
                    lon=[lon],
                    mode="markers+text",
                    marker=dict(size=22, color="crimson", opacity=1),
                    text=[f"{selected_state}: {humidity}%"],
                    textposition="top right",
                    hoverinfo="text"
                )
            )
            fig.update_layout(mapbox_center={"lat": lat, "lon": lon}, mapbox_zoom=6)
    return fig

# Page layout
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.H1("Humidity Levels", className="page-title"),
        html.P("Track changes in atmospheric moisture and its effects on climate, agriculture, and local weather.", className="info-text"),
        dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True),

        # New UI: live city humidity search
        html.Div([
            html.H3("Live City Humidity", className="live-data-title"),
            html.Div([
                dcc.Input(
                    id="live-city-input",
                    type="text",
                    placeholder="Enter city...",
                    className="input-style"
                ),
                html.Button("Get Live Humidity", id="fetch-live-data-btn", className="action-button"),
            ], className="input-group"),
            dcc.Loading(
                id="loading-live-humidity",
                type="circle",
                children=html.Div(id="live-humidity-output", className="api-output-box")
            ),
        ], className="live-data-container"),

        html.Hr(className="divider"),

        # Original UI: dropdown, map, and selected humidity readout
        html.Div([
            dcc.Dropdown(
                id="state-dropdown",
                options=[{"label": "All States", "value": "All"}] + sorted(
                    [{"label": s, "value": s} for s in _df_states["state"].tolist()],
                    key=lambda x: x["label"]
                ),
                value="All",
                clearable=False,
                searchable=True,
                placeholder="Select a state",
                style={"width": "320px", "minWidth": "220px", "whiteSpace": "normal"}
            ),
            dcc.Graph(
                id="humidity-map",
                figure=_build_figure(),
                config={"displayModeBar": False},
                style={"height": "520px", "marginTop": "12px"}
            ),
            html.Div(id="selected-humidity", className="info-text", style={"marginTop": "8px"})
        ], className="map-container")
    ], className="info-container")
], className="main-wrapper")

# Callback to update map and humidity readout based on dropdown selection
@dash.callback(
    Output("humidity-map", "figure"),
    Output("selected-humidity", "children"),
    Input("state-dropdown", "value"),
)
def update_map_and_readout(selected_state):
    fig = _build_figure(selected_state)
    if not selected_state or selected_state == "All":
        avg_hum = _df_states["humidity"].mean()
        text = f"Displaying all states — average humidity: {avg_hum:.1f}%"
    else:
        row = _df_states[_df_states["state"] == selected_state]
        if row.empty:
            text = "No data for selected state."
        else:
            text = f"{selected_state} — humidity: {int(row['humidity'].iloc[0])}%"
    return fig, text


# ✅ NEW: Callback to get and display live humidity from API
@dash.callback(
    Output("live-humidity-output", "children"),
    Input("fetch-live-data-btn", "n_clicks"),
    State("live-city-input", "value"),
    prevent_initial_call=True
)
def fetch_live_humidity(n_clicks, city):
    if not city:
        return html.Div("Please enter a city name.", className="api-info")

    weather_data = get_real_time_weather_data(city)

    if "error" in weather_data:
        return html.Div(weather_data["error"], className="api-error")
    else:
        humidity = weather_data.get("humidity_percent", "N/A")
        return html.Div(f"Live humidity in {weather_data['city']}: {humidity}%", className="api-success")