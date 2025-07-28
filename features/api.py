import requests
from tkinter import messagebox
import os

def fetch_owm_forecast(city_info):
    """
    Fetches 14-day weather forecast data from OpenWeatherMap's Daily Forecast API using lat/lon.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        messagebox.showerror("API Key Error", "OpenWeather API key not found. Check your .env file.")
        return None

    lat = city_info["lat"]
    lon = city_info["lon"]

    # URL for the 16-Day/Daily Forecast API
    url = "http://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "imperial",
        "cnt": 14  # Number of days to return (max 16)
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check for API-specific error code
        if data.get("cod") != "200":
            message = data.get('message', 'Unknown error')
            messagebox.showerror("Forecast Error", f"Forecast not found. API response: {message}")
            return None
        
        # Check if forecast list is present
        if "list" not in data or not data["list"]:
            messagebox.showerror("Forecast Error", "No forecast data found in the API response.")
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

def fetch_historical_forecast_data(latitude, longitude, start_date, end_date):
    """
    Fetches historical forecast data from the Open-Meteo API.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code,sunrise,sunset',
        'timezone': 'UTC',  # Ensure consistent timezone
        'temperature_unit': 'fahrenheit',
        'wind_speed_unit': 'mph',
        'precipitation_unit': 'inch'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical forecast data: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing historical forecast data: {e}")
        return None