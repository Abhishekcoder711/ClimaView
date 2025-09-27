import dash
from dash import dcc, html
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ✅ Flask server
server = Flask(__name__)
server.secret_key = "your_secret_key"
server.wsgi_app = ProxyFix(server.wsgi_app)

# ✅ Dash app
app = dash.Dash(
    __name__,
    use_pages=True,  # required for multi-page
    server=server,
    suppress_callback_exceptions=True
)

# ✅ App layout
app.layout = html.Div([
    dash.page_container
])

# Removed session/auth checks completely

if __name__ == "__main__":
    app.run(debug=True)
