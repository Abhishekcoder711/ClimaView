import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load API key from a .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# --- Function to get real-time temperature (from original dashboard.py) ---
import requests
import os

def get_real_time_temperature(city):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        return "Error: API key not found in environment variables."

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status() # Raises an HTTPError for bad responses
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error connecting to API: {e}"

    if data.get("cod") == 200:
        main = data["main"]
        temp = main["temp"]
        return temp # Return the number directly
    else:
        # Return a string message on error
        return f"Error: City '{city}' not found or invalid response."
# --- Function to get all real-time weather data for a single city ---
# This is the function used in humidity.py, rainfall.py, wind.py and seasonal.py
def get_real_time_weather_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    try:
        if not API_KEY:
            return {"error": "API Key not found. Please check your .env file."}

        url = f"{base_url}q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        if data.get("cod") != 200:
            return {"error": data.get("message", "City not found.")}

        weather_info = {
            "city": data['name'],
            "lat": data['coord']['lat'],
            "lon": data['coord']['lon'],
            "temp_celsius": data['main']['temp'],
            "humidity_percent": data['main']['humidity'],
            "weather_desc": data['weather'][0]['description'].capitalize(),
            # Wind data is in m/s, convert to km/h for readability
            "wind_speed_kmh": round(data['wind']['speed'] * 3.6, 2),
            "wind_speed_mps": data['wind']['speed'],
            "wind_direction_deg": data['wind'].get('deg', 'N/A')
        }
        
        # Add rainfall data if available, it's often optional in the API response
        if 'rain' in data and '1h' in data['rain']:
            weather_info['rain_1h'] = data['rain']['1h']
        elif 'rain' in data and '3h' in data['rain']:
            weather_info['rain_3h'] = data['rain']['3h']
            
        return weather_info
    
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# --- Function to get 5-day forecast data ---
# This function is used in projection.py
def get_5_day_forecast_data(city):
    """Fetches a 5-day, 3-hour forecast for a given city."""
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    try:
        if not API_KEY:
            return {"error": "API Key not found. Please check your .env file."}

        url = f"{base_url}q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        
        if data.get("cod") != "200":
            return {"error": data.get("message", "City not found.")}

        forecast_list = data["list"]
        forecast_data = []
        
        # OpenWeatherMap provides 3-hour intervals, we'll take one per day for simplicity
        seen_dates = set()
        for item in forecast_list:
            timestamp = datetime.fromtimestamp(item['dt'])
            date_str = timestamp.strftime('%Y-%m-%d')
            
            if date_str not in seen_dates:
                seen_dates.add(date_str)
                forecast_data.append({
                    "date": timestamp.strftime('%a, %b %d'),
                    "temp_celsius": item['main']['temp'],
                    "weather_desc": item['weather'][0]['description'].capitalize(),
                    "humidity_percent": item['main']['humidity'],
                    "wind_speed_kmh": round(item['wind']['speed'] * 3.6, 2)
                })
        
        return {"city": data['city']['name'], "forecast": forecast_data}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}