import dash
from dash import dcc, html, callback, Input, Output
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

dash.register_page(__name__, path='/sea-level', name='Sea Level')

# Common NOAA stations (station_id: location name)
STATIONS = {
    "8518750": "New York, NY",
    "9414290": "San Francisco, CA",
    "8771341": "Galveston, TX",
    "8410140": "Portland, ME",
    "8723214": "Naples, FL",
    "9432780": "Seattle, WA"
}

layout = html.Div([
    html.H1("🌊 Global Sea Level Trends", className="app-title"),
    html.Hr(style={"borderTop": "2px solid #bbb", "marginTop": "10px", "marginBottom": "20px"}),

    dcc.Link(
        html.Button("Go to Dashboard",
                    style={"backgroundColor": "#2C4057", "color": "white",
                           "padding": "10px", "border": "none",
                           "borderRadius": "10px", "cursor": "pointer"}),
        href="/dashboard", style={"marginTop": "20px"}),

    html.P("Analyze historical sea level data from NOAA.",
           style={"color": "white", "fontSize": "22px",
                  "marginBottom": "20px", "marginTop": "20px"}),

    html.Div([
        html.Label("📍 Select Station:",
                   style={"color": "white", "fontSize": "18px"}),
        dcc.Dropdown(
            id="station-dropdown",
            options=[{"label": f"{name} ({sid})", "value": sid} for sid, name in STATIONS.items()],
            value="8518750",  # default New York
            style={'width': '350px'}
        ),
        html.Label("📅 Select Year:",
                   style={"color": "white", "fontSize": "18px", "marginLeft": "30px"}),
        dcc.Dropdown(
            id="sea-label-year-dropdown",
            options=[{"label": str(y), "value": str(y)} for y in range(2000, 2025)],
            value='2014',
            style={'width': '120px'}
        ),
    ], style={"display": "flex", "alignItems": "center",
              "gap": "20px", "marginBottom": "20px"}),

    dcc.Graph(id="sea-level-graph", style={'marginTop': '30px', 'backgroundColor': "#7c7c7c"}),
    html.Div(id="error-message", style={'color': 'red', 'marginTop': '10px'})
], className="main-content")


@callback(
    Output("sea-level-graph", "figure"),
    Output("error-message", "children"),
    Input("sea-label-year-dropdown", "value"),
    Input("station-dropdown", "value")
)
def update_sea_level_graph(selected_year, station_id):
    api_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    try:
        # Prepare date range (Jan–Dec)
        start = datetime(int(selected_year), 1, 1)
        end = datetime(int(selected_year), 12, 31)
        all_data = []

        while start <= end:
            chunk_end = min(start + timedelta(days=30), end)
            params = {
                "begin_date": start.strftime("%Y%m%d"),
                "end_date": chunk_end.strftime("%Y%m%d"),
                "station": station_id,
                "product": "water_level",
                "datum": "MSL",
                "units": "metric",
                "time_zone": "gmt",
                "application": "Dash_App",
                "format": "json"
            }

            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                all_data.extend(data["data"])

            start = chunk_end + timedelta(days=1)

        if not all_data:
            return {}, f"No data available for {STATIONS[station_id]} in {selected_year}."

        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        df.rename(columns={'t': 'Date_Time', 'v': 'Water_Level'}, inplace=True)
        df['Date_Time'] = pd.to_datetime(df['Date_Time'])
        df['Water_Level'] = pd.to_numeric(df['Water_Level'])

        # Rolling average
        df['Rolling_Avg'] = df['Water_Level'].rolling(7, min_periods=1).mean()

        # Extremes
        high_water = df['Water_Level'].max()
        low_water = df['Water_Level'].min()
        high_date = df.loc[df['Water_Level'].idxmax(), 'Date_Time']
        low_date = df.loc[df['Water_Level'].idxmin(), 'Date_Time']

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date_Time'], y=df['Water_Level'],
                                 mode='lines', name='Daily Water Level',
                                 line=dict(color='cyan')))
        fig.add_trace(go.Scatter(x=df['Date_Time'], y=df['Rolling_Avg'],
                                 mode='lines', name='7-Day Avg',
                                 line=dict(color='orange', width=2)))
        fig.add_trace(go.Scatter(x=[high_date], y=[high_water],
                                 mode='markers+text', name='Max Level',
                                 marker=dict(color='red', size=10),
                                 text=["Max"], textposition='top center'))
        fig.add_trace(go.Scatter(x=[low_date], y=[low_water],
                                 mode='markers+text', name='Min Level',
                                 marker=dict(color='blue', size=10),
                                 text=["Min"], textposition='bottom center'))

        fig.update_layout(
            title=f"Sea Level at {STATIONS[station_id]} ({station_id}) - {selected_year}",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Date",
            yaxis_title="Water Level (m)",
            legend=dict(orientation="h", y=-0.2)
        )

        return fig, ""

    except requests.exceptions.RequestException as e:
        return {}, f"Failed to fetch data from NOAA: {e}"
    except Exception as e:
        return {}, f"An unexpected error occurred: {e}"
