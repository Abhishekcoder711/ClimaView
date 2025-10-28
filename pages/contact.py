import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State

dash.register_page(__name__)

layout = dbc.Container(
    [
        html.H1("Contact Us", className="text-center mb-4"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H2("Get in Touch", className="card-title"),
                            html.P("We'd love to hear from you! Use the form below to send us a message or reach out via the contact information provided."),
                            
                            html.Div([
                                html.I(className="fas fa-envelope contact-icon"),
                                html.A("support@climateview.com", href="mailto:support@climateview.com", className="contact-link")
                            ], className="contact-item"),

                            html.Div([
                                html.I(className="fas fa-phone contact-icon"),
                                html.Span("+1 (555) 123-4567", className="contact-link")
                            ], className="contact-item"),

                            html.Div([
                                html.I(className="fas fa-map-marker-alt contact-icon"),
                                html.Span("123 Mohali, Punjab, INDIA", className="contact-link")
                            ], className="contact-item"),
                        ])
                    ),
                    md=6,
                    className="d-flex flex-column"
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H2("Send us a Message", className="card-title"),
                            dbc.Form([
                                html.Div([
                                    html.Label("Name", htmlFor="contact-name", className="form-label"),
                                    dbc.Input(type="text", id="contact-name", placeholder="Your Name", className="mb-3"),
                                ], className="mb-3"),
                                html.Div([
                                    html.Label("Email", htmlFor="contact-email", className="form-label"),
                                    dbc.Input(type="email", id="contact-email", placeholder="Your Email", className="mb-3"),
                                ], className="mb-3"),
                                html.Div([
                                    html.Label("Message", htmlFor="contact-message", className="form-label"),
                                    dbc.Textarea(id="contact-message", placeholder="Your Message", style={"height": "120px"}, className="mb-3"),
                                ], className="mb-3"),
                                dbc.Button("Submit", color="primary", id="contact-submit", className="mt-2"),
                                html.Div(id="contact-output", className="mt-3")
                            ])
                        ])
                    ),
                    md=6,
                    className="d-flex flex-column"
                ),
            ],
            justify="center",
            className="gx-4"
        ),
    ],
    className="mt-5 contact-layout-wrapper",
    style={"maxWidth": "1000px"},
)

@callback(
    Output("contact-output", "children"),
    Input("contact-submit", "n_clicks"),
    State("contact-name", "value"),
    State("contact-email", "value"),
    State("contact-message", "value"),
    prevent_initial_call=True,
)
def submit_contact_form(n_clicks, name, email, message):
    if not name or not email or not message:
        return dbc.Alert("Please fill in all fields.", color="warning")
    return dbc.Alert(f"Thank you, {name}! Your message has been sent.", color="success")
