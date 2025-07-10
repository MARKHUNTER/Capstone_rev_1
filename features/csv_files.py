# features/csv_files.py
import csv
import os
from tkinter import messagebox
from features.config import get_om_weather_description

HISTORY_DIR = "historical_data" # Define the directory for historical CSVs
os.makedirs(HISTORY_DIR, exist_ok=True) # Ensure directory exists

def create_historical_data_csv(state_name, city_name, daily_weather_data, start_date_str, end_date_str):
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

    except IOError as e:
        messagebox.showerror("File Error", f"Could not write to file {output_filepath}: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while saving historical data: {e}")