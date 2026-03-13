import dash
from dash import dcc, html
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os
from flask import Flask, render_template

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ✅ Flask server
server = Flask(__name__)
server.secret_key = "your_secret_key"
server.wsgi_app = ProxyFix(server.wsgi_app)

# ✅ External stylesheets: Bootstrap + Font Awesome
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
]

# ✅ Dash app
app = dash.Dash(
    __name__,
    use_pages=True,  # required for multi-page
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)

# ✅ App layout
app.layout = html.Div([
    dash.page_container
])

@server.route("/privacy")
def privacy_policy():
    return render_template("privacy_policy.html")

if __name__ == "__main__":
    app.run(debug=True)