from dash import html, dcc, Input, Output, callback, State
import pandas as pd
import plotly.express as px
import dash
import os
from dotenv import load_dotenv

# Register the page
dash.register_page(__name__, path='/global-metrics', name='Global Metrics')

# Load climate data
df = pd.read_csv("data/climate.csv")
df["Year"] = df["Year"].astype(int)
ranked_df = df.copy()
ranked_df["Rank"] = ranked_df.groupby("Year")["Temperature"].rank(ascending=False)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

min_year = df["Year"].min()
max_year = df["Year"].max()

layout = html.Div([
    html.H1("Global Climate Metrics", className="app-title"),

    html.Hr(style={"borderTop": "2px solid #bbb", "marginTop":"10px", "marginBottom":"20px"}),
    dcc.Link(html.Button("Go to Dashboard"), href="/dashboard", style={"marginTop":"20px", "background-color":"#2C4057","color":"#2C4057","padding":"10px", "border":"none", "borderRadius":"10px", "cursor":"pointer"}),

    html.P("Explore detailed graphs and trends for global climate data.", className="description", style={"color": "white", "fontSize":"22px","marginBottom":"20px", "marginTop":"20px"}), 
    
    html.Div([
        html.Label("📅 Select Year:", style={"color": "white", "fontSize":"18px",}),
        dcc.Dropdown(
            id="year-dropdown-metrics",
            className="year-dropdown",style={"marginTop":"5px","marginBottom":"15px"},  # <--- यह नई क्लास जोड़ी गई है
            options=[{"label": str(y), "value": y} for y in range(min_year, max_year + 1)],
            value=min_year
        ),
    ]),

    html.Div([
        html.Label("Select Country:",style={"color": "white", "fontSize":"18px", "marginTop":"20px", "marginBottom":"20px"}),
        dcc.Dropdown(
            id="country-dropdown-metrics",
            className="year-dropdown",style={"marginTop":"5px"},  # <--- यह नई क्लास जोड़ी गई है
            options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
            value="India"
        ),

        html.Button(id="download-btn", children="Download Map", className="action-button",style={"marginTop":"20px", "marginBottom":"20px"}),
        dcc.Download(id="download-image"),
    ], style={"display": "left", "alignItems": "left", "gap": "20px","marginBottom": "20px"}),

    dcc.Graph(id="world-map-metrics", style={"marginTop":"30px"}),
    dcc.Graph(id="co2-graph-metrics",style={"marginTop":"30px"}),
    dcc.Graph(id="global-temp-trend-metrics",style={"marginTop":"30px"}),
    dcc.Graph(id="scatter-co2-temp-metrics",style={"marginTop":"30px"}),

], className="main-content")


# Download callback ko yahan shift kar diya gaya hai
@callback(
    Output("download-image", "data"),
    Input("download-btn", "n_clicks"),
    State("year-dropdown-metrics", "value"),
    prevent_initial_call=True
)
def download(n, year):
    f = df[df["Year"] == year]
    fig = px.choropleth(
        f,
        locations="Country",
        locationmode="country names",
        color="Temperature",
        hover_name="Country",
        color_continuous_scale="YlOrRd",
        title=f"Global Temperature in {year}"
    )
    return dcc.send_bytes(fig.to_image(format="png"), filename=f"map_{year}.png")


# Callbacks for the graphs on the new page

# World Map Callback (Using a better color scale)
@callback(
    Output("world-map-metrics", "figure"),
    Input("year-dropdown-metrics", "value")
)
def update_map(selected_year):
    filtered = ranked_df[ranked_df["Year"] == selected_year]
    fig = px.choropleth(
        filtered,
        locations="Country",
        locationmode="country names",
        color="CO2",
        hover_name="Country",
        hover_data={"Temperature": ":.2f", "CO2": ":.2f"},
        color_continuous_scale="Turbo", # Changed color scale
        title=f"🌏 Global CO₂ Emissions - {selected_year}"
    )
    fig.update_geos(
        visible=False, showcountries=True, countrycolor="gray", showocean=True, oceancolor="#b0e0e6",
        showland=True, landcolor="#f0e68c", showlakes=True, lakecolor="#add8e6", projection_type="natural earth"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=720)
    return fig

# CO₂ Graph Callback (Using an Area Chart)
@callback(
    Output("co2-graph-metrics", "figure"),
    Input("country-dropdown-metrics", "value")
)
def update_co2_graph(country):
    cdf = df[df["Country"] == country]
    fig = px.area(cdf, x="Year", y="CO2", title=f"📊 CO₂ Emissions Over Time — {country}") # Changed to area chart
    fig.update_traces(fill='tozeroy') # Optional: Fills the area to zero y-axis
    return fig

# Temp Trend Callback (Using a Smoothed Line)
@callback(
    Output("global-temp-trend-metrics", "figure"),
    Input("year-dropdown-metrics", "value")
)
def temp_trend(_):
    avg_df = df.groupby("Year")["Temperature"].mean().reset_index()
    fig = px.line(avg_df, x="Year", y="Temperature", title="Global Average Temperature Over Time (with 10-Year Rolling Average)")
    
    # Add a rolling average line for better trend visualization
    avg_df['Rolling_Temp'] = avg_df['Temperature'].rolling(window=10).mean()
    fig.add_scatter(x=avg_df['Year'], y=avg_df['Rolling_Temp'], mode='lines', name='10-Year Rolling Average',
                     line=dict(color='red', width=3))
    return fig

# Scatter Callback (Using a Bubble Chart)
@callback(
    Output("scatter-co2-temp-metrics", "figure"),
    Input("year-dropdown-metrics", "value")
)
def scatter(year):
    f = df[df["Year"] == year]
    
    fig = px.scatter(
        f, x="CO2", y="Temperature", size="CO2", color="Country",
        hover_name="Country", title=f"📉 CO₂ vs Temperature by CO₂ Emission — {year}"
    )
    return fig