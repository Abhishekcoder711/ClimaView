import copy
import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path='/temperature', name='Temperature Trends')

# Sample state-centroid temperature data (avg annual °C)
_state_temp_list = [
    {"state": "Andhra Pradesh", "lat": 16.51, "lon": 80.62, "temp": 28.0},
    {"state": "Arunachal Pradesh", "lat": 27.09, "lon": 93.61, "temp": 18.5},
    {"state": "Assam", "lat": 26.15, "lon": 91.77, "temp": 24.0},
    {"state": "Bihar", "lat": 25.61, "lon": 85.13, "temp": 26.5},
    {"state": "Chhattisgarh", "lat": 21.25, "lon": 81.63, "temp": 25.0},
    {"state": "Goa", "lat": 15.49, "lon": 73.83, "temp": 27.5},
    {"state": "Gujarat", "lat": 23.22, "lon": 72.65, "temp": 27.0},
    {"state": "Haryana", "lat": 29.06, "lon": 76.08, "temp": 25.5},
    {"state": "Himachal Pradesh", "lat": 31.10, "lon": 77.17, "temp": 15.0},
    {"state": "Jharkhand", "lat": 23.34, "lon": 85.33, "temp": 25.5},
    {"state": "Karnataka", "lat": 12.97, "lon": 77.59, "temp": 26.0},
    {"state": "Kerala", "lat": 8.52, "lon": 76.92, "temp": 27.8},
    {"state": "Madhya Pradesh", "lat": 23.25, "lon": 77.41, "temp": 26.0},
    {"state": "Maharashtra", "lat": 19.07, "lon": 72.87, "temp": 27.0},
    {"state": "Manipur", "lat": 24.82, "lon": 93.94, "temp": 23.5},
    {"state": "Meghalaya", "lat": 25.57, "lon": 91.88, "temp": 20.5},
    {"state": "Mizoram", "lat": 23.73, "lon": 92.72, "temp": 23.0},
    {"state": "Nagaland", "lat": 25.67, "lon": 94.12, "temp": 22.5},
    {"state": "Odisha", "lat": 20.27, "lon": 85.84, "temp": 27.0},
    {"state": "Punjab", "lat": 30.74, "lon": 76.79, "temp": 24.5},
    {"state": "Rajasthan", "lat": 26.91, "lon": 75.79, "temp": 27.0},
    {"state": "Sikkim", "lat": 27.33, "lon": 88.61, "temp": 16.5},
    {"state": "Tamil Nadu", "lat": 13.08, "lon": 80.27, "temp": 28.0},
    {"state": "Telangana", "lat": 17.38, "lon": 78.48, "temp": 27.0},
    {"state": "Tripura", "lat": 23.84, "lon": 91.28, "temp": 25.0},
    {"state": "Uttar Pradesh", "lat": 26.85, "lon": 80.95, "temp": 26.5},
    {"state": "Uttarakhand", "lat": 30.32, "lon": 78.03, "temp": 18.0},
    {"state": "West Bengal", "lat": 22.57, "lon": 88.36, "temp": 26.5},
    {"state": "Jammu & Kashmir", "lat": 34.08, "lon": 74.79, "temp": 10.5},
    {"state": "Ladakh", "lat": 34.16, "lon": 77.58, "temp": 2.0},
]

_df_temp_states = pd.DataFrame(_state_temp_list)

# Build initial Plotly mapbox figure for temperature
_fig_temp_base = px.scatter_mapbox(
    _df_temp_states,
    lat="lat",
    lon="lon",
    hover_name="state",
    hover_data={"temp": True, "lat": False, "lon": False},
    size="temp",
    color="temp",
    color_continuous_scale="Inferno",
    size_max=30,
    zoom=4,
    center={"lat": 22.0, "lon": 82.0},
)
_fig_temp_base.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Average Annual Temperature by State (sample, °C)",
)

# Map component for temperature
india_temp_map = dcc.Graph(id="india-temperature-map", figure=_fig_temp_base, config={"displayModeBar": True})

# Updated layout: include temperature map, dropdown and details under same info-container
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.H1("Temperature Trends", className="page-title"),
        html.P("Analyze long-term temperature shifts, heatwaves, and seasonal variations. Compare historical data to recent trends.", className="info-text"),
        dcc.Link(html.Button("← Back to Dashboard", className="action-button back-button"), href="/dashboard", refresh=True)
    ], className="info-container"),

    # Added temperature map and details section
    html.Div([html.H2("India — Statewise Temperature Map"), india_temp_map], className="map-container"),
    html.Div([
        html.H2("State-wise Temperature Details"),
        html.Div([
            html.Label("Search by state:"),
            dcc.Dropdown(
                id="temp-state-select",
                options=[{"label": s["state"], "value": s["state"]} for s in _state_temp_list],
                value=_state_temp_list[0]["state"],
                clearable=False,
                searchable=True,
                style={"width": "340px"},
            ),
            html.Div(id="temp-state-details", style={"marginTop": "12px"}),
        ], className="details-container"),
    ], className="details-section"),
], className="main-wrapper")


# Callback: pan/zoom temperature map to selected state
@dash.callback(
    Output("india-temperature-map", "figure"),
    Input("temp-state-select", "value"),
)
def _pan_to_temp_state(selected):
    row = _df_temp_states[_df_temp_states["state"] == selected]
    if row.empty:
        return _fig_temp_base
    lat = float(row["lat"].iloc[0])
    lon = float(row["lon"].iloc[0])
    fig = copy.deepcopy(_fig_temp_base)
    fig.update_layout(mapbox_center={"lat": lat, "lon": lon}, mapbox=dict(center={"lat": lat, "lon": lon}, zoom=6))
    fig.update_traces(marker=dict(opacity=0.9))
    return fig

# Callback: show selected state's temperature details
@dash.callback(Output("temp-state-details", "children"), Input("temp-state-select", "value"))
def _update_temp_state_details(selected_state):
    row = _df_temp_states[_df_temp_states["state"] == selected_state].squeeze()
    if row.empty:
        return html.Div("State not found")
    return html.Table([
        html.Tr([html.Th("State:"), html.Td(row["state"])]),
        html.Tr([html.Th("Avg annual temperature (°C):"), html.Td(float(row["temp"]))]),
        html.Tr([html.Th("Latitude:"), html.Td(row["lat"])]),
        html.Tr([html.Th("Longitude:"), html.Td(row["lon"])]),
    ], style={"border": "none", "marginTop": "6px"})