import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div(className="about-layout-wrapper", children=[
    dbc.Container(className="about-page-container", children=[
        html.Section(className="about-header-section", children=[
            html.H1("About ClimaView", className="about-header-title"),
            html.P("Understanding Our Climate, Shaping Our Future", className="about-header-subtitle"),
        ]),

        dbc.Row(className="about-content-row", children=[
            dbc.Col(md=6, children=[
                dbc.Card(className="about-card primary-card", children=[
                    html.H2("Our Mission", className="about-section-heading"),
                    html.P("To empower individuals and organizations with accessible, insightful climate data, fostering informed decisions and promoting sustainable practices.", className="about-section-text"),
                    html.Ul(className="about-list", children=[
                        html.Li("Provide accurate and reliable climate information."),
                        html.Li("Visualize complex data in an easy-to-understand format."),
                        html.Li("Promote climate awareness and education."),
                        html.Li("Support data-driven solutions for a sustainable future."),
                    ]),
                ]),
            ]),
            dbc.Col(md=6, children=[
                dbc.Card(className="about-card secondary-card", children=[
                    html.H2("What We Offer", className="about-section-heading"),
                    html.P("ClimaView offers a comprehensive suite of tools and resources for exploring climate data:", className="about-section-text"),
                    html.Ul(className="about-list", children=[
                        html.Li("Interactive climate visualizations."),
                        html.Li("Real-time temperature updates."),
                        html.Li("Historical climate data analysis."),
                        html.Li("Educational resources and insights."),
                    ]),
                ]),
            ]),
        ]),

        html.Section(className="about-full-section", children=[
            html.H2("Meet the Team", className="about-section-heading"),
            dbc.Row(justify="center", children=[
                dbc.Col(md=4, children=[
                    dbc.Card(className="team-member-card", children=[
                        html.H4("Abhishek Kumar Mishra"),
                        html.P("Data Analyst & Backend Architect"),
                        html.P(""),
                        html.P("Abhishek is responsible for data collection, processing, and ensuring the integrity of our climate datasets. With a background in data science, he designs the backend architecture that powers our visualizations. His expertise ensures that our users receive accurate and up-to-date climate information."),
                    ]),
                ]),
                dbc.Col(md=4, children=[
                    dbc.Card(className="team-member-card", children=[
                        html.H4("Akhil Bhushan"),
                        html.P("UI/UX Design Lead & Front-End Integrator"),
                        html.P(""),
                        html.P("Akhil leads the design and user experience of ClimaView. He creates intuitive interfaces and ensures that our visualizations are not only informative but also engaging. His work focuses on making complex climate data accessible to users of all backgrounds."),
                    ]),
                ]),
                dbc.Col(md=4, children=[
                    dbc.Card(className="team-member-card", children=[
                        html.H4("Seeram Pavani"),
                        html.P("Front-End Developer & Visualization Specialist"),
                        html.P(""),
                        html.P("Seeram is responsible for implementing the front-end components of ClimaView. He specializes in creating dynamic and interactive visualizations that bring climate data to life. His work ensures that users can explore and understand climate trends through engaging visual representations."),
                    ]),
                ]),
            ]),
        ]),

        html.Section(className="about-cta-section", children=[
            html.H2("Ready to Explore Climate Data?", className="contact-prompt-heading"),
            html.P("Dive into our interactive dashboards and discover the insights that matter to you.", className="about-section-text"),
            dbc.Button("Explore Now", color="primary", size="lg", className="large-button", href="/dashboard"),
        ]),
    ]),
])