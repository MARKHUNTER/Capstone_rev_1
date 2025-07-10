# features/api.py
import requests
from tkinter import messagebox
import os # Needed to get API key from environment (loaded in main.py)

# OpenWeatherMap API Key is loaded in main.py and available via os.getenv
# The constant OPENWEATHER_API_KEY from config is not directly used here
# as it's meant for global scope, but os.getenv is runtime safe.

def fetch_owm_forecast(lat, lon):
    """
    Fetches 7-day weather forecast data from OpenWeatherMap API using lat/lon.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY") # Get API key when function is called
    if not api_key:
        messagebox.showerror("API Key Error", "OpenWeather API key not found. Check your .env file.")
        return None

    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("cod") != "200":
            message = data.get('message', 'Unknown error')
            messagebox.showerror("Forecast Error", f"Forecast not found. API response: {message}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not connect to OpenWeatherMap API: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while fetching forecast: {e}")
        return None


def fetch_historical_daily_data(lat, lon, timezone, start_date_str, end_date_str):
    """
    Fetches ONLY DAILY historical weather data for a given location and date range
    from Open-Meteo.com.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "wind_speed_10m_max", "sunrise", "sunset"
        ],
        "start_date": start_date_str,
        "end_date": end_date_str,
        "timezone": timezone,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not connect to Open-Meteo API: {e}")
        return None
    except KeyError as e:
        messagebox.showerror("Data Error", f"Unexpected data format from Open-Meteo API (missing key: {e}).")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while fetching historical data: {e}")
        return None