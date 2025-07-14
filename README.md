Code Overview
This code  is a weather application designed to provide weather information. It offers two main functionalities: a 7-day weather forecast and the display of monthly average temperatures derived from historical data. The application uses tkinter for its graphical user interface and matplotlib for plotting charts. It interacts with external APIs to fetch live weather forecasts from OpenWeatherMap and historical weather data from Open-Meteo. Historical data is then stored locally in CSV files for persistence and analysis. The project is structured into several Python modules within the features directory, separating concerns such as API interactions, CSV file handling, and UI tab functionalities. There is also a historical_data directory where the downloaded CSV files are stored.
Features
•	7-Day Weather Forecast: Provides a detailed forecast for selected cities.
•	Monthly Average Temperatures: Displays historical monthly average temperatures using charts.
•	City Selection: Allows users to select from a predefined list of states and cities.
•	Historical Data Management: Fetches and stores historical weather data in local CSV files to minimize repeated API calls.
•	Interactive Charts: Visualizes monthly average temperatures using matplotlib.
•	User-Friendly Interface: Built with tkinter for an intuitive graphical experience.
Project Structure and Modules
main.py
This is the main entry point of the application. It sets up the Python environment by adding the features directory to the path, loads environment variables (crucial for API keys), initializes the main Tkinter application window, and starts the GUI event loop.
features/api.py
This module handles interactions with external weather APIs. It provides two functions: fetch_owm_forecast for retrieving current and 7-day forecast data from OpenWeatherMap (requiring an API key) and fetch_historical_daily_data for fetching historical weather data from Open-Meteo (which does not require an API key). Both functions handle potential API errors and display messages to the user.
features/config.py
This module stores static configuration data, including a dictionary of states and cities with their respective geographical coordinates and timezones (STATE_CITY_DATA). It also defines a mapping of Open-Meteo weather codes to descriptive strings and emojis (OWM_WEATHER_EMOJIS) and includes a utility function get_om_weather_description to retrieve these descriptions. Lastly, it attempts to set up a suitable emoji font for cross-platform compatibility within the Tkinter application.
features/csv_files.py
This module is responsible for handling historical weather data in CSV files. It ensures that a historical_data directory exists. The create_historical_data_csv function takes daily weather data, sanitizes city and state names for filenames, and then either creates a new CSV file or appends to an existing one. It prevents duplicate entries by checking for existing dates in the CSV before writing new data.
features/forecast_tab.py
This class creates the "7-Day Weather Forecast" tab within the GUI. It includes dropdowns for state and city selection, a button to trigger the forecast retrieval, and a display area for the weather information. It uses fetch_owm_forecast to get current weather data and then displays the next 7 days' forecast, including max/min temperatures and a weather description with an emoji. It also includes a helper function get_owm_weather_description to translate OpenWeatherMap weather codes into more readable descriptions and emojis.
features/historical_tab.py
This class creates the "Monthly Average Temperatures" tab. It provides dropdowns for state, city, and year selection, and a button to generate a chart. When the "Get Monthly Averages Chart" button is clicked, the application first attempts to load historical data for the selected year from a local CSV file. If the data is not found or is incomplete, it fetches the full historical data from the Open-Meteo API, saves it to a CSV file, and then reloads the data for the selected year. It calculates monthly average temperatures from this data and displays them as a bar chart using matplotlib. The chart's title dynamically updates to show the data range used.


Organization of files:

WeatherApp/
├── main.py
└── features/
    ├── api.py
    ├── config.py
    ├── csv_files.py
    ├── forecast_tab.py
    ├── historical_tab.py
    └── main_app.py