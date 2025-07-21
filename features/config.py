# features/config.py
from datetime import datetime, timedelta
import matplotlib.font_manager as fm

# Data structure for States and Cities with coordinates and timezones.
STATE_CITY_DATA = {
    "New York": {
        "New York City": {"lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
        "Buffalo": {"lat": 42.8864, "lon": -78.8784, "timezone": "America/New_York"},
        "Yonkers": {"lat": 40.9312, "lon": -73.8260, "timezone": "America/New_York"},
        "Rochester": {"lat": 43.1566, "lon": -77.6088, "timezone": "America/New_York"},
        "Queens": {"lat": 40.7282, "lon": -73.7949, "timezone": "America/New_York"},
    },
    "California": {
        "Los Angeles": {"lat": 34.0522, "lon": -118.2437, "timezone": "America/Los_Angeles"},
        "San Diego": {"lat": 32.7157, "lon": -117.1611, "timezone": "America/Los_Angeles"},
        "San Jose": {"lat": 37.3382, "lon": -121.8863, "timezone": "America/Los_Angeles"},
        "San Francisco": {"lat": 37.7749, "lon": -122.4194, "timezone": "America/Los_Angeles"},
    },
    "Texas": {
        "Houston": {"lat": 29.7604, "lon": -95.3698, "timezone": "America/Chicago"},
        "San Antonio": {"lat": 29.4241, "lon": -98.4936, "timezone": "America/Chicago"},
        "Dallas": {"lat": 32.7767, "lon": -96.7970, "timezone": "America/Chicago"},
        "Austin": {"lat": 30.2672, "lon": -97.7431, "timezone": "America/Chicago"},
    },
    "Florida": {
        "Jacksonville": {"lat": 30.3322, "lon": -81.6557, "timezone": "America/New_York"},
        "Miami": {"lat": 25.7617, "lon": -80.1918, "timezone": "America/New_York"},
        "Tampa": {"lat": 27.9478, "lon": -82.4584, "timezone": "America/New_York"},
        "Orlando": {"lat": 28.5383, "lon": -81.3792, "timezone": "America/New_York"},
    },
    "Illinois": {
        "Chicago": {"lat": 41.8781, "lon": -87.6298, "timezone": "America/Chicago"},
        "Aurora": {"lat": 41.7606, "lon": -88.3201, "timezone": "America/Chicago"},
        "Rockford": {"lat": 42.2711, "lon": -89.0940, "timezone": "America/Chicago"},
        "Joliet": {"lat": 41.5250, "lon": -88.0833, "timezone": "America/Chicago"},
    },
    "Arizona": {
        "Phoenix": {"lat": 33.4484, "lon": -112.0740, "timezone": "America/Phoenix"},
        "Tucson": {"lat": 32.2226, "lon": -110.9747, "timezone": "America/Phoenix"},
        "Mesa": {"lat": 33.4152, "lon": -111.8315, "timezone": "America/Phoenix"},
        "Chandler": {"lat": 33.3062, "lon": -111.8413, "timezone": "America/Phoenix"},
    },
    "Pennsylvania": {
        "Philadelphia": {"lat": 39.9526, "lon": -75.1652, "timezone": "America/New_York"},
        "Pittsburgh": {"lat": 40.4406, "lon": -79.9959, "timezone": "America/New_York"},
        "Allentown": {"lat": 40.6084, "lon": -75.4700, "timezone": "America/New_York"},
        "Erie": {"lat": 42.1292, "lon": -80.0850, "timezone": "America/New_York"},
    }
}

# Mapping for weather descriptions to both emojis and colors (for OpenWeatherMap Forecast)
OWM_WEATHER_EMOJIS = {
    'clear sky': ('☀️', '#FFD700'),
    'few clouds': ('🌤️', '#87CEEB'),
    'scattered clouds': ('⛅', '#B0C4DE'),
    'broken clouds': ('☁️', '#A9A9A9'),
    'overcast clouds': ('☁️', '#808080'),
    'light rain': ('🌦️', '#00BFFF'),
    'moderate rain': ('🌧️', '#4682B4'),
    'heavy rain': ('⛈️', '#1E90FF'),
    'snow': ('🌨️', '#FFFFFF'),
    'mist': ('🌫️', '#C0C0C0'),
    'thunderstorm': ('⛈️', '#8B0000')
}

# Mapping for Open-Meteo weather codes to descriptions
OM_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense",
    61: "Rain: Light",
    63: "Rain: Moderate",
    65: "Rain: Heavy",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy",
    71: "Snow fall: Light",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy",
    77: "Snow grains",
    80: "Rain showers: Light",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Light",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Light/Moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_om_weather_description(code):
    """Translates Open-Meteo weather codes to human-readable descriptions."""
    return OM_WEATHER_CODES.get(code, f"Unknown ({code})")

# Load Segoe UI Emoji font globally if available (for Matplotlib)
emoji_font = None
for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    if "seguiemj" in font.lower():
        emoji_font = font
        break