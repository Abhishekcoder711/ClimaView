from dash import html, dcc, dash_table, Input, Output, callback
import pandas as pd
import dash

# Register the page
dash.register_page(__name__, path='/data-table', name='Data Table')

# Load the climate data
df = pd.read_csv("data/climate.csv")
df["Year"] = df["Year"].astype(int)

# English language support
languages = {
    "EN": {
        "title": "Climate Data Table",
        "select_year": "📅 Select Year:",
        "select_country": "Select Country:",
    }
}

min_year = df["Year"].min()
max_year = df["Year"].max()

layout = html.Div([
    html.H1("Climate Data Table", className="app-title"),

    html.Hr(style={"borderTop": "2px solid #bbb", "marginTop":"10px", "marginBottom":"20px"}),
    dcc.Link(html.Button("Go to Dashboard"), href="/dashboard", style={"marginTop":"20px", "background-color":"#2C4057","color":"#2C4057","padding":"10px", "border":"none", "borderRadius":"10px", "cursor":"pointer"}),

    html.P("View and filter historical climate data by year and country.", className="description", style={"color": "white", "fontSize":"20px","marginBottom":"20px", "marginTop":"20px"}),

    html.Div([
        html.Div([
            html.Label("📅 Select Year:", style={"color": "white", "fontSize":"18px",}),            dcc.Dropdown(
                id="year-dropdown-table",
                className="year-dropdown",  # <--- यह नई क्लास जोड़ी गई है
                options=[{"label": str(y), "value": y} for y in range(min_year, max_year + 1)],
                value=min_year
            )
        ], className="dropdown-container", style={"flex": "1"}),
        
        html.Div([
            html.Label("Select Country:",style={"color": "white", "fontSize":"18px", "marginTop":"10px", "marginBottom":"30px"}),
            dcc.Dropdown(
                id="country-dropdown-table",
                className="year-dropdown",  # <--- यह नई क्लास जोड़ी गई है
                options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
                value="India"
            )
        ], className="dropdown-container", style={"flex": "1"})
    ], className="selectors-row"),
    
    html.H2("Filtered Data", style={"fontSize": "24px", "marginTop": "30px", "color": "white"}),
    
    dash_table.DataTable(
        id="data-table-page",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=[],
        page_size=10,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"}
    )
], className="page-content")

@callback(
    Output("data-table-page", "data"),
    Input("year-dropdown-table", "value"),
    Input("country-dropdown-table", "value")
)
def update_data_table_page(selected_year, selected_country):
    filtered_df = df[(df["Year"] == selected_year) & (df["Country"] == selected_country)]
    return filtered_df.to_dict("records")