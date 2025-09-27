import dash
from dash import html, dcc, Input, Output
import datetime

dash.register_page(__name__, path="/")

# Define image URLs for the gallery
climate_images = [
    {
        'src': '/assets/glacier.png',
        'alt': 'Melting Glacier',
        'caption': 'Glacier Melting'
    },
    {
        'src': '/assets/forest_fire.png',
        'alt': 'Forest Fire',
        'caption': 'Forest Fire'
    },
    # {
    #     'src': '/assets/desertification.png',
    #     'alt': 'Desertification',
    #     'caption': 'Desertification'
    # },
    {
        'src': '/assets/sea_level.png',
        'alt': 'Rising Sea Level',
        'caption': 'Rising Sea Level'
    },
    {
        'src': '/assets/co2_emissions.png',
        'alt': 'CO2 Emissions Chart',
        'caption': 'CO2 Emissions'
    },
    {
        'src': '/assets/renewable_energy.png',
        'alt': 'Renewable Energy',
        'caption': 'Renewable Energy'
    },
    {
        'src': '/assets/desert_life.png',
        'alt': 'Desert Life',
        'caption': 'Desert Life'
    },
    #  {
    #     'src': '/assets/sea_level(1980).png',
    #     'alt': 'Sea Level Rise',
    #     'caption': 'Sea Level Rise'
    # },
     {
        'src': '/assets/earth_atmosphere.png',
        'alt': 'Earth Atmosphere',
        'caption': 'Earth Atmosphere'
    },
    #  {
    #     'src': '/assets/air_pollution.png',
    #     'alt': 'Air Pollution',
    #     'caption': 'Air Pollution'
    # },
    # {
    #     'src': '/assets/poison.png',
    #     'alt': 'Poison',
    #     'caption': 'Poison'
    # },
    {
        'src': '/assets/car_pollution.png',
        'alt': 'Car Pollution',
        'caption': 'Car Pollution'
    }
]
# Page layout
layout = html.Div([
    html.Div(className="sky"),
    html.Div([
        html.Div(id="live-datetime", style={"position": "absolute", "top": "15px", "right": "15px", "fontSize": "12px", "color": "#fff"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),

        html.H1("Welcome to Climate Data Visualizer", style={"textAlign": "center", "color": "rgb(14, 30, 51)", "marginTop": "40px"}),
        html.H2("ClimaView", style={"textAlign": "center", "fontSize": "28px", "color": "#2C4057", "fontfamily": "Bold", "marginTop": "10px"}),
        html.P("!!Explore weather patterns, climate trends, and more!!", style={"textAlign": "center", "fontSize": "20px", "marginTop": "20px", "color": "#1d2f4a"}),
        html.P("Your one-stop solution for climate data insights", style={"textAlign": "center", "fontSize": "18px", "color": "#1d2f4a"}),
        
        # Go to Dashboard Button
        html.Div([
            dcc.Link(html.Button("Go to Dashboard", id="to-dashboard", className="action-button"), href="/dashboard", refresh=True)
        ], style={"textAlign": "center", "marginTop": "30px"}),

        # Our Mission & Climate Knowledge Section
        html.Div([
            html.H2("Our Mission & Climate Knowledge", className="section-heading", style={"color": "#194638"}),
            html.P(
                "Our mission is to empower individuals and organizations with easy-to-understand climate data. "
                "By visualizing complex trends, we hope to inspire action and promote a deeper understanding of climate change.",
                className="intro-text"
            ),
            html.Div([
                html.Div([
                    html.I(className="fas fa-thermometer-half", style={"fontSize": "24px"}),
                    html.H4("Global Temperature Rise"),
                    html.P(
                        "The Earth's average temperature has risen by approximate 11&deg;C since the pre-industrial era, with human activities being the primary cause. "
                        "This warming is directly linked to an increase in the frequency and intensity of extreme weather events,"
                        "such as more severe heatwaves, droughts, and flooding. These changes are also leading to shifts in climate zones,"
                        "impacting ecosystems and agriculture worldwide."),
                ], className="knowledge-block"),
                html.Div([
                    html.I(className="fas fa-cloud", style={"fontSize": "24px"}),
                    html.H4("CO₂ Levels"),
                    html.P("Atmospheric carbon dioxide ($CO₂$) levels have reached their highest point in over 800,000 years."
                           " This increase is primarily due to the burning of fossil fuels, deforestation, and other human activities."
                           " Elevated $CO₂$ levels contribute to the greenhouse effect, trapping heat in the atmosphere and leading to global warming."
                           "$CO₂$ is a potent greenhouse gas that traps heat in the Earth's atmosphere, leading to the overall warming of the planet."),
                ], className="knowledge-block"),
                html.Div([
                    html.I(className="fas fa-water", style={"fontSize": "24px"}),
                    html.H4("Rising Sea Levels"),
                    html.P("Global sea levels have been rising at an accelerating rate due to thermal expansion and melting ice."
                           "Thermal Expansion: As ocean water warms from climate change, it expands in volume, causing sea levels to rise."
                           "Melting Ice: The rapid melting of glaciers and ice sheets in polar regions, such as Antarctica and Greenland, adds a large volume of water to the oceans."
                           "This continuous rise in sea levels poses a significant threat to coastal communities, ecosystems, and infrastructure around the globe."),
                ], className="knowledge-block"),
            ], className="climate-knowledge-container"),
        ], className="intro-section"),

        html.Hr(style={'margin-top': '40px', 'margin-bottom': '40px'}),

        # Climate Gallery
        html.Div([
            html.H2("Our Gallery", className="gallery-heading"),
            html.Div(
                [
                    html.Div([
                        html.Img(src=img['src'], alt=img['alt'], className="gallery-image"),
                        html.P(img['caption'], className="gallery-caption")
                    ], className="image-container") for img in climate_images
                ],
                className="gallery-grid"
            )
        ], className="climate-gallery-section"),

        html.Hr(style={'margin-top': '40px', 'margin-bottom': '40px'}),
    ], className="main-wrapper")
])

@dash.callback(
    Output("live-datetime", "children"),
    Input("interval-clock", "n_intervals")
)
def update_clock(n):
    now = datetime.datetime.now().strftime("%A, %d %B %Y | %I:%M:%S %p")
    return now
