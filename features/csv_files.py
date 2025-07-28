# features/csv_files.py
import csv
import os
from tkinter import messagebox
from datetime import datetime, timedelta
from features.config import get_om_weather_description
from features.api import fetch_historical_forecast_data  # Import the API function

HISTORY_DIR = "historical_data" # Define the directory for historical CSVs
os.makedirs(HISTORY_DIR, exist_ok=True) # Ensure directory exists

def clean_data(csv_filepath):
    """
    Removes all rows in a CSV file after the first row containing missing data.

    Args:
        csv_filepath (str): The path to the CSV file.
    """

    rows = []
    missing_data_found = False

    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Read the header row
            rows.append(header)

            for row in reader:
                if any(not cell.strip() for cell in row):  # Check for empty cells
                    missing_data_found = True
                    break  # Stop adding rows after the first row with missing data
                else:
                    rows.append(row)

        # Write the filtered rows back to the CSV file
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        print(f"Cleaned data in {csv_filepath}")

    except FileNotFoundError:
        print(f"Error: File not found at {csv_filepath}")
    except Exception as e:
        print(f"Error cleaning data in {csv_filepath}: {e}")

def create_historical_data_csv(state_name, city_name, daily_weather_data, start_date_str, end_date_str, state_city_data):
    """
    Takes daily weather data from Open-Meteo and saves/appends it to a CSV file.
    Ensures only one reading per day, specifically the daily aggregated data.
    Filename format: state_city_daily_weather_history.csv
    """
    if not daily_weather_data or 'daily' not in daily_weather_data:
        messagebox.showwarning("No Data", f"No daily weather data available for {city_name} for the period {start_date_str} to {end_date_str}.")
        return

    # MODIFIED FILENAME FORMAT
    filename = f"{state_name.replace(' ', '_').lower()}_{city_name.replace(' ', '_').lower()}_daily_weather_history.csv"
    output_filepath = os.path.join(HISTORY_DIR, filename)

    daily = daily_weather_data['daily']

    fieldnames = [
        "Date", "Max Temperature (°F)", "Min Temperature (°F)",
        "Precipitation (inch)", "Max Wind Speed (mph)",
        "Weather Description", "Sunrise (UTC)", "Sunset (UTC)"
    ]

    rows_to_write = []
    num_days = len(daily['time'])

    for i in range(num_days):
        weather_code = daily['weather_code'][i]
        description = get_om_weather_description(weather_code)
        
        row = {
            "Date": daily['time'][i],
            "Max Temperature (°F)": daily['temperature_2m_max'][i],
            "Min Temperature (°F)": daily['temperature_2m_min'][i],
            "Precipitation (inch)": daily['precipitation_sum'][i],
            "Max Wind Speed (mph)": daily['wind_speed_10m_max'][i],
            "Weather Description": description,
            "Sunrise (UTC)": daily['sunrise'][i],
            "Sunset (UTC)": daily['sunset'][i]
        }
        rows_to_write.append(row)

    try:
        file_exists = os.path.exists(output_filepath)
        
        # Read existing dates for de-duplication
        existing_dates = set()
        if file_exists:
            try:
                with open(output_filepath, 'r', newline='', encoding='utf-8') as read_f:
                    reader = csv.DictReader(read_f)
                    # Check if header matches to avoid reading malformed files
                    if reader.fieldnames == fieldnames:
                        for r in reader:
                            existing_dates.add(r['Date'])
                    else:
                        print(f"Warning: Header mismatch in {output_filepath}. Overwriting file.")
                        file_exists = False
            except Exception as read_e:
                print(f"Warning: Could not read existing file {output_filepath} for de-duplication: {read_e}. Appending all new data for this session.")
                existing_dates = set()

        new_rows = [row for row in rows_to_write if row['Date'] not in existing_dates]

        with open(output_filepath, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            if new_rows:
                writer.writerows(new_rows)
                messagebox.showinfo("Success", f"Daily historical data for {city_name} ({state_name}) from {start_date_str} to {end_date_str} saved/appended to:\n{output_filepath}\nAdded {len(new_rows)} new entries.")
            else:
                messagebox.showinfo("Info", f"No new daily historical data to add for {city_name} ({state_name}) from {start_date_str} to {end_date_str}). File is up-to-date for this period.")

        # Clean the data immediately after creating the CSV file
        clean_data(output_filepath)

        # --- Fill in Missing Last Days ---
        # Extract latitude and longitude from city data (replace with your actual data source)
        # This assumes you have a way to access STATE_CITY_DATA from this module
        #from features.main_app import STATE_CITY_DATA, selected_state_name # Import here to avoid circular dependencies
        city_info = state_city_data.get(state_name, {}).get(city_name)
        if city_info:
            latitude = city_info['lat']
            longitude = city_info['lon']

            # Determine the last date in the CSV file
            last_date_str = None
            try:
                with open(output_filepath, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    if rows:
                        last_date_str = rows[-1]['Date']  # Get the date from the last row
            except Exception as e:
                print(f"Error reading CSV to determine last date: {e}")
                last_date_str = None

            # Convert start and end dates to datetime objects for comparison
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            if last_date_str:
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
                next_date = last_date + timedelta(days=1)

                # Fetch data for missing days (up to the specified end date or tomorrow, whichever is earlier)
                missing_end_date = min(end_date, tomorrow)  # Ensure we don't exceed the intended end date
                if next_date <= missing_end_date:
                    missing_start_date_str = next_date.strftime('%Y-%m-%d')
                    missing_end_date_str = missing_end_date.strftime('%Y-%m-%d')

                    # --- DIAGNOSTIC ---
                    yesterday = today - timedelta(days=1)
                    missing_start_date_str = yesterday.strftime('%Y-%m-%d')
                    missing_end_date_str = yesterday.strftime('%Y-%m-%d')
                    print(f"*** API DIAGNOSTIC ***: Requesting data for: {missing_start_date_str}")
                    # --- END DIAGNOSTIC ---

                    historical_forecast_data = fetch_historical_forecast_data(latitude, longitude, missing_start_date_str, missing_end_date_str)

                    if historical_forecast_data and 'daily' in historical_forecast_data:
                        daily_forecast = historical_forecast_data['daily']
                        num_missing_days = len(daily_forecast['time'])
                        print(f"num_missing_days: {num_missing_days}")

                        missing_rows_to_write = []
                        for i in range(num_missing_days):
                            weather_code = daily_forecast['weather_code'][i]
                            description = get_om_weather_description(weather_code)

                            missing_row = {
                                "Date": daily_forecast['time'][i],
                                "Max Temperature (°F)": daily_forecast['temperature_2m_max'][i],
                                "Min Temperature (°F)": daily_forecast['temperature_2m_min'][i],
                                "Precipitation (inch)": daily_forecast['precipitation_sum'][i],
                                "Max Wind Speed (mph)": daily_forecast['wind_speed_10m_max'][i],
                                "Weather Description": description,
                                "Sunrise (UTC)": daily_forecast['sunrise'][i],
                                "Sunset (UTC)": daily_forecast['sunset'][i]
                            }
                            print(f"missing_row: {missing_row}") # ADDED: Check the row data

                            missing_rows_to_write.append(missing_row)

                        # --- DIAGNOSTIC: Check fieldnames and data types ---
                        print(f"fieldnames: {fieldnames}")
                        for row in missing_rows_to_write:
                            for key, value in row.items():
                                print(f"Key: {key}, Value: {value}, Type: {type(value)}")
                        # --- END DIAGNOSTIC ---

                        # Append the missing rows to the CSV file
                        with open(output_filepath, 'a', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writerows(missing_rows_to_write)

                        print(f"Appended {len(missing_rows_to_write)} missing days to {output_filepath}")
                        clean_data(output_filepath) # Clean again after appending
                    else:
                        print("No historical forecast data found for the missing days.")
            else:
                print("Could not determine the last date in the CSV file.")
        else:
            print(f"City information not found for {city_name}, {state_name}. Cannot fetch missing data.")

    except IOError as e:
        messagebox.showerror("File Error", f"Could not write to file {output_filepath}: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while saving historical data: {e}")