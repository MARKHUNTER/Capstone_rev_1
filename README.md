## Code Overview
This code  is a weather application designed to provide weather information. It offers two main functionalities: up to a  14-day weather forecast and the display of monthly average temperatures derived from historical data. The application uses tkinter for its graphical user interface and matplotlib for plotting charts. It interacts with external APIs to fetch live weather forecasts from OpenWeatherMap and historical weather data from Open-Meteo. Historical data is then stored locally in CSV files for persistence and analysis. The project is structured into several Python modules within the features directory, separating concerns such as API interactions, CSV file handling, and UI tab functionalities. There is also a historical_data directory where the downloaded CSV files are stored.

## Features
• Up to a 14 Day Weather Forecast: Provides a temperature forcast for selected cities.
• Monthly Average Temperatures: Displays historical monthly average temperatures using charts.
• City Selection: Allows users to select from a predefined list of states and cities.
• Historical Data Management: Fetches and stores historical weather data in local CSV files to minimize repeated API calls.
• Interactive Charts: Visualizes monthly average temperatures using matplotlib.
• Team Tab Multi-City Comparison: The Team tab now supports selecting multiple cities via checkboxes and displays their data on the same chart for comparison.
• Chart Type Selection: Dropdowns allow switching between bar and line charts for both monthly and daily data.
• Dynamic Chart Updates: All chart controls (city, variable, chart type, scroll/slider) update the chart automatically without needing a button.
• Dynamic Chart Titles: Daily line charts on the Team tab display a dynamic title showing the date range of the current scroll position.
• Compact, Organized UI: The Team tab UI is organized with grouped controls and a compact layout for ease of use.
• User-Friendly Interface: Built with tkinter for an intuitive graphical experience.

## Project Structure, Modules, and Tab Layouts

### main.py
This is the main entry point of the application. It sets up the Python environment by adding the features directory to the path, loads environment variables (crucial for API keys), initializes the main Tkinter application window, and starts the GUI event loop.

### features/api.py
This module handles interactions with external weather APIs. It provides two functions: fetch_owm_forecast for retrieving current and 7-day forecast data from OpenWeatherMap (requiring an API key) and fetch_historical_daily_data for fetching historical weather data from Open-Meteo (which does not require an API key). Both functions handle potential API errors and display messages to the user.

### features/config.py
This module stores static configuration data, including a dictionary of states and cities with their respective geographical coordinates and timezones (STATE_CITY_DATA). It also defines a mapping of Open-Meteo weather codes to descriptive strings and emojis (OWM_WEATHER_EMOJIS) and includes a utility function get_om_weather_description to retrieve these descriptions. Lastly, it attempts to set up a suitable emoji font for cross-platform compatibility within the Tkinter application.

### features/csv_files.py
This module is responsible for handling historical weather data in CSV files. It ensures that a historical_data directory exists. The create_historical_data_csv function takes daily weather data, sanitizes city and state names for filenames, and then either creates a new CSV file or appends to an existing one. It prevents duplicate entries by checking for existing dates in the CSV before writing new data.

### features/forecast_tab.py
This class creates the "7-Day Weather Forecast" tab within the GUI. It uses a simple vertical layout: dropdowns for state and city selection are placed at the top, followed by a button to trigger the forecast retrieval, and a display area for the weather information below. This tab uses the pack geometry manager for a straightforward, stacked appearance.

### features/historical_tab.py
This class creates the "Monthly Average Temperatures" tab. It uses a form-like layout with dropdowns for state, city, and year selection at the top, and a button to generate the chart. The chart appears below the controls. This tab uses a mix of pack and grid geometry managers to align controls and chart output, providing a clear separation between input and visualization.

### features/team_tab.py
This module implements the Team tab, which uses a compact, grid-based layout. Controls for city selection (checkboxes), variable selection (radio buttons), and chart type (dropdown) are grouped in labeled frames at the top. The chart area is below, with a horizontal scroll/slider for daily charts. All controls update the chart automatically—no button is required. This tab uses the grid geometry manager for precise placement and grouping of controls, supporting multi-city comparison and dynamic chart updates.

## Organization of files:

WeatherApp/
├── main.py
├── features/
│   ├── api.py
│   ├── config.py
│   ├── csv_files.py
│   ├── forecast_tab.py
│   ├── historical_tab.py
│   ├── team_tab.py
│   └── main_app.py
├── historical_data

