# features/historical_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import csv
import os

# Import from local features package
from features.config import STATE_CITY_DATA
from features.api import fetch_historical_daily_data
from features.csv_files import HISTORY_DIR, create_historical_data_csv


class HistoricalTab(ttk.Frame):
    def __init__(self, notebook, parent_root):
        super().__init__(notebook)
        self.parent_root = parent_root
        self.create_widgets()

    def create_widgets(self):
        # Updated header label
        header_label = tk.Label(self, text="Monthly Average Temperatures from CSV", font=("Arial", 20, "bold"), bg="#f3e7a3")
        header_label.pack(fill=tk.X, pady=10)

        # Frame for State and City dropdowns (similar to ForecastTab)
        dropdown_frame = tk.Frame(self)
        dropdown_frame.pack(pady=5)

        tk.Label(
            dropdown_frame,
            text="Select State:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        # FIX: Initialize self.state_var and self.city_var at the very top of create_widgets
        self.state_var = tk.StringVar(self)
        self.city_var = tk.StringVar(self)

        self.states = sorted(list(STATE_CITY_DATA.keys()))
        self.state_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.state_var,
            values=self.states,
            state="readonly",
            font=("Arial", 14)
        )
        self.state_dropdown.pack(side=tk.LEFT, padx=5)
        if self.states:
            self.state_var.set(self.states[0])

        tk.Label(
            dropdown_frame,
            text="Select City:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        self.city_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.city_var, # Correctly linked to self.city_var
            values=[], # Initial empty values, will be populated by update_cities_dropdown
            state="readonly",
            font=("Arial", 14)
        )
        self.city_dropdown.pack(side=tk.LEFT, padx=5)

        self.state_dropdown.bind("<<ComboboxSelected>>", self.update_cities_dropdown)
        self.update_cities_dropdown() # Initial call to populate cities for default state

        # Button for getting monthly average chart
        style = ttk.Style()
        style.configure('Rounded.TButton',
            padding=6,
            relief="raised",
            foreground="#000000",
            background="#ADD8E6",
            font=('Arial', 12, 'bold')
        )
        self.get_chart_btn = ttk.Button(dropdown_frame, text="Get Monthly Averages", style='Rounded.TButton', width=20, command=self.get_monthly_average_chart)
        self.get_chart_btn.pack(side=tk.LEFT, padx=10)

        # Frame for matplotlib graph
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(pady=10, fill="both", expand=True)

        # Status Label
        self.status_label = ttk.Label(self, text="Ready.")
        self.status_label.pack(pady=5)

    def update_cities_dropdown(self, event=None):
        selected_state = self.state_var.get()
        cities_in_state = sorted(list(STATE_CITY_DATA.get(selected_state, {}).keys()))
        self.city_dropdown['values'] = cities_in_state
        if cities_in_state:
            self.city_var.set(cities_in_state[0]) # Correctly using self.city_var.set()
        else:
            self.city_var.set("") # Correctly using self.city_var.set()

    def get_monthly_average_chart(self):
        selected_state_name = self.state_var.get()
        selected_city_name = self.city_var.get() # Correctly accessing self.city_var here

        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Processing...")
        self.get_chart_btn.config(state=tk.DISABLED)
        self.parent_root.update_idletasks()

        if not selected_city_name:
            messagebox.showwarning("Selection Error", "Please select a city.")
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        city_info = STATE_CITY_DATA.get(selected_state_name, {}).get(selected_city_name)
        if not city_info:
            messagebox.showerror("Error", "City data not found for the selected state/city combination.")
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        lat = city_info["lat"]
        lon = city_info["lon"]
        timezone = city_info["timezone"]

        # Construct CSV file path
        filename = f"{selected_state_name.replace(' ', '_').lower()}_{selected_city_name.replace(' ', '_').lower()}_daily_weather_history.csv"
        csv_filepath = os.path.join(HISTORY_DIR, filename)

        all_daily_data = []

        # --- Check if CSV exists and read it, or fetch if not ---
        if not os.path.exists(csv_filepath) or os.path.getsize(csv_filepath) == 0:
            messagebox.showinfo("Data Not Found", f"Historical data file not found or is empty for {selected_city_name} ({selected_state_name}).\nAttempting to fetch full historical data now...")
            self.status_label.config(text=f"Fetching ALL historical data for {selected_city_name}...")
            self.parent_root.update_idletasks()

            # Define specific historical range for import: July 1, 2024 to yesterday
            import_start_date = datetime(2024, 7, 1).date()
            import_end_date = datetime.now().date() - timedelta(days=1) # Yesterday's date

            if import_start_date > import_end_date:
                tk.Label(self.graph_frame, text=f"Historical data import range for {selected_city_name} is invalid (start date {import_start_date} is after end date {import_end_date}). No data to fetch.", fg="red").pack()
                self.status_label.config(text="Ready.")
                self.get_chart_btn.config(state=tk.NORMAL)
                return

            import_start_date_str = import_start_date.isoformat()
            import_end_date_str = import_end_date.isoformat()

            historical_weather_data = fetch_historical_daily_data(
                lat, lon, timezone, import_start_date_str, import_end_date_str
            )

            if historical_weather_data and 'daily' in historical_weather_data:
                create_historical_data_csv(
                    selected_state_name, selected_city_name, historical_weather_data,
                    import_start_date_str, import_end_date_str
                )
                # Now that it's created/updated, try to read it again
                try:
                    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            all_daily_data.append(row)
                except Exception as e:
                    messagebox.showerror("Read Error", f"Failed to read newly created CSV file: {e}")
                    self.status_label.config(text="Ready.")
                    self.get_chart_btn.config(state=tk.NORMAL)
                    return
            else:
                messagebox.showwarning("Import Failed", f"Could not fetch historical data to create CSV for {selected_city_name}.")
                self.status_label.config(text="Ready.")
                self.get_chart_btn.config(state=tk.NORMAL)
                return
        else:
            # If CSV exists, read it
            try:
                with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        all_daily_data.append(row)
            except Exception as e:
                messagebox.showerror("Error Reading CSV", f"An error occurred while reading the CSV file: {e}")
                self.status_label.config(text="Ready.")
                self.get_chart_btn.config(state=tk.NORMAL)
                return
        
        # --- Process all data from CSV for Monthly Averages ---
        if not all_daily_data:
            tk.Label(self.graph_frame, text="No historical data available to calculate monthly averages.", fg="red").pack()
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        monthly_temps_sum = defaultdict(float)
        monthly_temps_count = defaultdict(int)
        
        # Determine the full date range covered by the loaded data
        min_date_loaded = datetime.max.date()
        max_date_loaded = datetime.min.date()

        for row in all_daily_data:
            date_str = row.get('Date')
            max_temp_str = row.get('Max Temperature (°F)')
            min_temp_str = row.get('Min Temperature (°F)')

            if not date_str or not max_temp_str or not min_temp_str:
                continue # Skip rows with missing essential data

            try:
                date_obj = datetime.fromisoformat(date_str).date()
                max_temp = float(max_temp_str)
                min_temp = float(min_temp_str)
            except (ValueError, TypeError):
                continue # Skip rows with malformed data

            min_date_loaded = min(min_date_loaded, date_obj)
            max_date_loaded = max(max_date_loaded, date_obj)

            month_year = date_obj.strftime("%Y-%m")
            daily_avg_temp = (max_temp + min_temp) / 2
            
            monthly_temps_sum[month_year] += daily_avg_temp
            monthly_temps_count[month_year] += 1

        monthly_averages = {}
        for month_year in sorted(monthly_temps_sum.keys()):
            if monthly_temps_count[month_year] > 0:
                monthly_averages[month_year] = monthly_temps_sum[month_year] / monthly_temps_count[month_year]
        
        if not monthly_averages:
            tk.Label(self.graph_frame, text="No sufficient data from CSV to calculate monthly averages.", fg="red").pack()
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        months = list(monthly_averages.keys())
        avg_temps = list(monthly_averages.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#c8c8f3")
        ax.set_facecolor("#f3e7a3")
        for spine in ax.spines.values():
            spine.set_visible(False)

        bars = ax.bar(months, avg_temps, color='#ADD8E6')
        ax.set_ylabel("Average Temperature (°F)")
        
        # Adjusted title to reflect full historical range from CSV
        title_start_date = min_date_loaded.strftime("%Y-%m-%d") if monthly_averages else "N/A"
        title_end_date = max_date_loaded.strftime("%Y-%m-%d") if monthly_averages else "N/A"
        ax.set_title(f"Monthly Average Temperatures for {selected_city_name}\n(Data from {title_start_date} to {title_end_date})", pad=20)
        
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=60, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 1), ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
        self.status_label.config(text="Chart generated from CSV.")

        self.get_chart_btn.config(state=tk.NORMAL)