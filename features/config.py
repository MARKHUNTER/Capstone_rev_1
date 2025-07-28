# features/config.py
from datetime import datetime, timedelta
import matplotlib.font_manager as fm

# Data structure for States and Cities with coordinates and timezones.
STATE_CITY_DATA = {
    "New York": {
        "New York City": {"name":"New York City", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
        "Buffalo": {"name":"Buffalo", "lat": 42.8864, "lon": -78.8784, "timezone": "America/New_York"},
        "Yonkers": {"name":"Yonkers", "lat": 40.9312, "lon": -73.8260, "timezone": "America/New_York"},
        "Rochester": {"name":"Rochester", "lat": 43.1566, "lon": -77.6088, "timezone": "America/New_York"},
        "Queens": {"name":"Queens", "lat": 40.7282, "lon": -73.7949, "timezone": "America/New_York"},
        "Bronx": {"name":"Bronx", "lat": 40.8448, "lon": -73.8648, "timezone": "America/New_York"},
    },
    "California": {
        "Los Angeles": {"name":"Los Angeles", "lat": 34.0522, "lon": -118.2437, "timezone": "America/Los_Angeles"},
        "San Diego": {"name":"San Diego", "lat": 32.7157, "lon": -117.1611, "timezone": "America/Los_Angeles"},
        "San Jose": {"name":"San Jose", "lat": 37.3382, "lon": -121.8863, "timezone": "America/Los_Angeles"},
        "San Francisco": {"name":"San Francisco", "lat": 37.7749, "lon": -122.4194, "timezone": "America/Los_Angeles"},
    },
    "Texas": {
        "Houston": {"name":"Houston", "lat": 29.7604, "lon": -95.3698, "timezone": "America/Chicago"},
        "San Antonio": {"name":"San Antonio", "lat": 29.4241, "lon": -98.4936, "timezone": "America/Chicago"},
        "Dallas": {"name":"Dallas", "lat": 32.7767, "lon": -96.7970, "timezone": "America/Chicago"},
        "Austin": {"name":"Austin", "lat": 30.2672, "lon": -97.7431, "timezone": "America/Chicago"},
    },
    "Florida": {
        "Jacksonville": {"name":"Jacksonville", "lat": 30.3322, "lon": -81.6557, "timezone": "America/New_York"},
        "Miami": {"name":"Miami", "lat": 25.7617, "lon": -80.1918, "timezone": "America/New_York"},
        "Tampa": {"name":"Tampa", "lat": 27.9478, "lon": -82.4584, "timezone": "America/New_York"},
        "Orlando": {"name":"Orlando", "lat": 28.5383, "lon": -81.3792, "timezone": "America/New_York"},
    },
    "Illinois": {
        "Chicago": {"name":"Chicago", "lat": 41.8781, "lon": -87.6298, "timezone": "America/Chicago"},
        "Aurora": {"name":"Aurora", "lat": 41.7606, "lon": -88.3201, "timezone": "America/Chicago"},
        "Rockford": {"name":"Rockford", "lat": 42.2711, "lon": -89.0940, "timezone": "America/Chicago"},
        "Joliet": {"name":"Joliet", "lat": 41.5250, "lon": -88.0833, "timezone": "America/Chicago"},
    },
    "Arizona": {
        "Phoenix": {"name":"Phoenix", "lat": 33.4484, "lon": -112.0740, "timezone": "America/Phoenix"},
        "Tucson": {"name":"Tucson", "lat": 32.2226, "lon": -110.9747, "timezone": "America/Phoenix"},
        "Mesa": {"name":"Mesa", "lat": 33.4152, "lon": -111.8315, "timezone": "America/Phoenix"},
        "Chandler": {"name":"Chandler", "lat": 33.3062, "lon": -111.8413, "timezone": "America/Phoenix"},
    },
    "Pennsylvania": {
        "Philadelphia": {"name":"Philadelphia", "lat": 39.9526, "lon": -75.1652, "timezone": "America/New_York"},
        "Pittsburgh": {"name":"Pittsburgh", "lat": 40.4406, "lon": -79.9959, "timezone": "America/New_York"},
        "Allentown": {"name":"Allentown", "lat": 40.6084, "lon": -75.4700, "timezone": "America/New_York"},
        "Erie": {"name":"Erie", "lat": 42.1292, "lon": -80.0850, "timezone": "America/New_York"},
    }
}

# Mapping for weather descriptions to both emojis and colors (for OpenWeatherMap Forecast)
OWM_WEATHER_EMOJIS = {
    "clear sky": ("☀️", "#FFE600"),
    "sky is clear": ("☀️", "#FFE600"),  # Add this line
    "few clouds": ("🌤️", "#1E90FF"),
    "scattered clouds": ("🌤️", "#1E90FF"),
    "broken clouds": ("⛅", "#4682B4"),
    "overcast clouds": ("☁️", "#808080"),
    "light rain": ("🌦️", "#00BFFF"),
    "moderate rain": ("🌧️", "#4169E1"),
    "heavy intensity rain": ("🌧️", "#4169E1"),
    "very heavy rain": ("🌧️", "#4169E1"),
    "extreme rain": ("🌧️", "#4169E1"),
    "freezing rain": ("🌧️", "#4169E1"),
    "light intensity shower rain": ("🌦️", "#00BFFF"),
    "shower rain": ("🌧️", "#4169E1"),
    "heavy intensity shower rain": ("🌧️", "#4169E1"),
    "light snow": ("🌨️", "#A9A9A9"),
    "snow": ("🌨️", "#A9A9A9"),
    "heavy snow": ("🌨️", "#A9A9A9"),
    "sleet": ("🌨️", "#A9A9A9"),
    "light shower sleet": ("🌨️", "#A9A9A9"),
    "shower sleet": ("🌨️", "#A9A9A9"),
    "light rain and snow": ("🌨️", "#A9A9A9"),
    "rain and snow": ("🌨️", "#A9A9A9"),
    "light intensity drizzle": ("🌦️", "#00BFFF"),
    "drizzle": ("🌦️", "#00BFFF"),
    "heavy intensity drizzle": ("🌦️", "#00BFFF"),
    "light intensity drizzle rain": ("🌦️", "#00BFFF"),
    "drizzle rain": ("🌦️", "#00BFFF"),
    "heavy intensity drizzle rain": ("🌦️", "#00BFFF"),
    "shower rain and drizzle": ("🌦️", "#00BFFF"),
    "shower drizzle": ("🌦️", "#00BFFF"),
    "thunderstorm": ("⛈️", "#8B0000"),
    "mist": ("🌫️", "#A0522D"),
    "smoke": ("🌫️", "#A0522D"),
    "haze": ("🌫️", "#A0522D"),
    "sand/dust whirls": ("🌫️", "#A0522D"),
    "fog": ("🌫️", "#A0522D"),
    "sand": ("🌫️", "#A0522D"),
    "dust": ("🌫️", "#A0522D"),
    "volcanic ash": ("🌋", "#B22222"),
    "squalls": ("🌪️", "#696969"),
    "tornado": ("🌪️", "#696969"),
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