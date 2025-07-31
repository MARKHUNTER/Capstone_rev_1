# Copilot Instructions for Capstone Weather Application

## Project Overview
This project is a Tkinter-based weather dashboard for visualizing weather data (historical and forecast) for various US cities. It uses Matplotlib for charting and pandas for data manipulation (in some tabs). Data is sourced from OpenWeatherMap and Open-Meteo APIs, with local CSV caching for historical data. The codebase is modular, with each major UI tab in its own file under `features/`.

## Directory Structure
- `main.py`: Application entry point; sets up Tkinter root and loads the main app.
- `features/`: Contains all main logic modules:
  - `api.py`: API calls for weather data (OpenWeatherMap, Open-Meteo).
  - `config.py`: Centralized city/state data, emoji mapping, and config constants.
  - `csv_files.py`: Handles reading/writing historical weather CSVs.
  - `forecast_tab.py`: 7-day forecast tab logic.
  - `historical_tab.py`: Historical data tab (monthly/daily charts, scrolling, error handling).
  - `team_tab.py`: Team weather data tab (city/variable selection, chart type toggle, pandas-based).
  - `main_app.py`: Main Tkinter app and tab setup.
- `historical_data/`, `GroupData/`, etc.: CSV data files for historical and team weather.

## Coding Conventions
- **UI**: Use Tkinter and ttk for widgets. Use `FigureCanvasTkAgg` for embedding Matplotlib charts.
- **Data**: Use pandas for advanced data manipulation (e.g., grouping, monthly averages) in team tab; use csv module or pandas in other tabs as appropriate.
- **Error Handling**: Always use `try/except` for file/data operations. Use `messagebox` for user-facing errors.
- **Config**: All city/state/coordinate data should be in `features/config.py`.
- **Tab Structure**: Each tab should be a class, instantiated and added to the main app in `main_app.py`.
- **Charting**: For daily charts with many data points, implement horizontal scrolling using a Tkinter Canvas and embed the Matplotlib figure.
- **Data Caching**: Always check for local CSV before making API calls for historical data.

## Workflow for New Features
1. Add new tab logic as a class in `features/`.
2. Register the new tab in `main_app.py`.
3. For new data sources, add API logic to `api.py` and update config/constants as needed.
4. For new cities/states, update `STATE_CITY_DATA` in `config.py`.
5. For new chart types, follow the Matplotlib embedding pattern in existing tabs.

## Testing & Debugging
- Test UI changes by running `main.py`.
- For pandas errors (e.g., groupby, duplicate columns), check for column name collisions and use `.copy()` when needed.
- Validate CSV file structure before loading; handle missing/extra columns gracefully.

## AI Agent Guidance
- **When adding features:** Follow the modular tab pattern; do not put all logic in `main.py`.
- **When fixing bugs:** Prefer minimal, targeted changes; preserve error handling and user feedback.
- **When handling data:** Always sanitize user input and file paths; avoid hardcoding file names.
- **When updating charts:** Ensure the chart is cleared/redrawn, and scrolling is preserved for large datasets.
- **When using pandas:** Avoid duplicate column names after merges/groupbys; use `reset_index()` and explicit column renaming if needed.

## Example: Adding a New Tab
1. Create `features/new_tab.py` with a class for the tab.
2. Add the tab to the notebook in `main_app.py`.
3. Use config/constants from `config.py`.
4. Use error handling/messagebox for all file/data operations.

## Contact & Ownership
- For questions about city/state data, see `features/config.py`.
- For API issues, see `features/api.py`.
- For UI/feature bugs, see the relevant tab file in `features/`.

---
_Last updated: 2024-06_
