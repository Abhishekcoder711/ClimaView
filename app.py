import dash
from dash import dcc, html
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os
from flask import Flask, render_template
from flask import send_from_directory

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ✅ Flask server
server = Flask(__name__)
server.secret_key = os.getenv("SECRET_KEY", "dev_secret")
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

app.index_string = """
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>ClimaView - Climate Data Visualization Dashboard</title>

<meta name="description" content="ClimaView is an interactive climate data visualization dashboard to explore temperature, rainfall, humidity, wind, and global climate metrics." />

<meta name="keywords" content="climate data dashboard, weather analytics, climate visualization, temperature trends, rainfall data, climate insights" />

<meta name="author" content="Abhishek Kumar Mishra">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="canonical" href="https://climaview-vc1d.onrender.com">

<meta name="robots" content="index, follow">

<meta property="og:title" content="ClimaView - Climate Data Visualization Dashboard">
<meta property="og:description" content="Explore climate data insights including temperature, rainfall, humidity and wind trends through interactive visualizations.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://climaview-vc1d.onrender.com">
<meta property="og:image" content="https://climaview-vc1d.onrender.com/assets/earth_atmosphere.png">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ClimaView Climate Dashboard">
<meta name="twitter:description" content="Interactive dashboard to explore climate data trends and weather insights.">
<meta name="twitter:image" content="https://climaview-vc1d.onrender.com/assets/earth_atmosphere.png">

<meta name="theme-color" content="#0a2540">
<meta name="google-adsense-account" content="ca-pub-1256249325677007">

{%favicon%}
{%css%}

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1256249325677007"
crossorigin="anonymous"></script>

</head>
<body>
{%app_entry%}
<!-- ClimaView-Ad -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-1256249325677007"
     data-ad-slot="9501225380"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
<footer>
{%config%}
{%renderer%}
</footer>
</body>
</html>
"""

# ✅ App layout
app.layout = html.Div([
    dash.page_container
])

@server.route("/privacy")
def privacy_policy():
    return render_template("privacy_policy.html")


@server.route('/ads.txt')
def ads_txt():
    return send_from_directory('.', 'ads.txt')

if __name__ == "__main__":
    app.run(debug=False)