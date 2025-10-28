import requests
import os
from dotenv import load_dotenv 

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY") 

def get_weather_news():
    if not GNEWS_API_KEY:
        return {"error": "GNEWS_API_KEY not found in .env file."}

    keywords = "weather OR climate OR forecast OR cyclone OR monsoon OR flood"
    
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": keywords,
        "lang": "en",
        "country": "in",
        "max": 5, 
        "token": GNEWS_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10) 
        response.raise_for_status() 
        data = response.json()
        
        news_list = []
        if data.get('articles'):
            for article in data['articles']:
                news_list.append({
                    'title': article['title'],
                    'url': article['url'],
                    'source': article['source']['name']
                })
        
        return news_list
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching news: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}