# # features/forecast_tab.py
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import matplotlib.font_manager as fm

# Import from local features package
from features.config import STATE_CITY_DATA, OWM_WEATHER_EMOJIS, emoji_font
from features.api import fetch_owm_forecast, fetch_historical_daily_data
from features.csv_files import create_historical_data_csv


class ForecastTab(ttk.Frame):
    def __init__(self, parent_notebook):
        super().__init__(parent_notebook)
        self.parent_notebook = parent_notebook
        self.STATE_CITY_DATA = STATE_CITY_DATA  # Add this line
        self.create_widgets()

    def create_widgets(self):
        # Label for Forcast Tab
        header_label = tk.Label(self, text="Forecast For Selected Cities", font=("Arial", 20, "bold"), bg="#8baaed")
        header_label.pack(fill=tk.X, pady=10)

        dropdown_frame = tk.Frame(self)
        dropdown_frame.pack(pady=5)

        tk.Label(
            dropdown_frame,
            text="Select State:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.state_var = tk.StringVar()
        self.states = sorted(list(STATE_CITY_DATA.keys()))
        self.state_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.state_var,
            values=self.states,
            state="readonly",
            font=("Arial", 14),
            width=8  # ADDED: Adjust width as needed
        )
        self.state_dropdown.pack(side=tk.LEFT, padx=5)
        if self.states:
            self.state_var.set(self.states[0])

        tk.Label(
            dropdown_frame,
            text="Select City:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.city_var,
            state="readonly",
            font=("Arial", 14),
            width=8  # ADDED: Adjust width as needed
        )
        self.city_dropdown.pack(side=tk.LEFT, padx=5)

        # --- Number of Days Dropdown ---
        tk.Label(
            dropdown_frame,
            text="Select Days:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.num_days_var = tk.StringVar()
        self.num_days_values = ["3","5","7","9","10","11","12","13","14"]  # Options for number of days
        self.num_days_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.num_days_var,
            values=self.num_days_values,
            state="readonly",
            font=("Arial", 14),
            width=5  # ADDED: Adjust width as needed
        )
        self.num_days_dropdown.pack(side=tk.LEFT, padx=5)
        self.num_days_var.set("7")  # Default value
        # --- End Number of Days Dropdown ---

        self.state_dropdown.bind("<<ComboboxSelected>>", self.update_cities_dropdown)
        self.update_cities_dropdown()

        # --- Chart Type Radio Buttons ---
        self.chart_type = tk.StringVar(value="bar")  # Default to bar chart

        chart_type_frame = tk.Frame(dropdown_frame)
        chart_type_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(chart_type_frame, text="Chart Type:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        bar_radio = tk.Radiobutton(chart_type_frame, text="Bar Chart", variable=self.chart_type, value="bar", font=("Arial", 12))
        bar_radio.pack(side=tk.LEFT)

        line_radio = tk.Radiobutton(chart_type_frame, text="Line Chart", variable=self.chart_type, value="line", font=("Arial", 12))
        line_radio.pack(side=tk.LEFT)
        # --- End Chart Type Radio Buttons ---

        style = ttk.Style()
        style.configure('Rounded.TButton',
            padding=6,
            relief="raised",
            foreground="#000000",
            background="#8baaed",
            font=('Arial', 12, 'bold')
        )
        # Update Chart
        get_btn = ttk.Button(dropdown_frame, text="Update Chart", style='Rounded.TButton', width=15, command=self.get_weekly_forecast)
        get_btn.pack(side=tk.LEFT, padx=10)

        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(pady=10, fill="both", expand=True)

    def update_cities_dropdown(self, event=None):
        selected_state = self.state_var.get()
        cities_in_state = sorted(list(STATE_CITY_DATA.get(selected_state, {}).keys()))
        self.city_dropdown['values'] = cities_in_state
        if cities_in_state:
            self.city_var.set(cities_in_state[0])
        else:
            self.city_var.set('')

    def get_weekly_forecast(self):
        selected_state_name = self.state_var.get()
        selected_city_name = self.city_var.get()
        num_forecast_days = int(self.num_days_var.get()) # Get the selected number of days
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if not selected_city_name:
            tk.Label(self.graph_frame, text="Please select a city.", fg="red").pack()
            return

        city_info = STATE_CITY_DATA.get(selected_state_name, {}).get(selected_city_name)
        if not city_info:
            tk.Label(self.graph_frame, text="Selected city data not found.", fg="red").pack()
            return

        lat = city_info["lat"]
        lon = city_info["lon"]
        timezone = city_info["timezone"]

        # --- Fetch 14-Day Forecast (OpenWeatherMap Daily Forecast API) ---
        forecast_data = fetch_owm_forecast(city_info)

        if forecast_data:
            # The daily forecast data is in the 'list' key
            daily_forecasts = forecast_data["list"][:num_forecast_days] # Limit to selected number of days

            # --- Add current weather summary boxes (using the first day's forecast data) ---
            current_day_data = daily_forecasts[0]
            curr_temp_max = current_day_data["temp"]["max"]
            curr_temp_min = current_day_data["temp"]["min"]
            curr_precip = current_day_data.get("pop", 0) * 100
            curr_wind = current_day_data["speed"] # Key is 'speed' in this API response
            curr_desc = current_day_data["weather"][0]["description"].capitalize()

            summary_frame = tk.Frame(self.graph_frame)
            summary_frame.pack(pady=10)

            # --- Weather Icon and Description ---
            weather_emoji, weather_color = OWM_WEATHER_EMOJIS.get(curr_desc.lower(), ('❓', '#CCCCCC'))
            weather_text = f"{curr_desc}\n{weather_emoji}"

            emoji_box = tk.Label(summary_frame, text=weather_text, font=("Arial", 16, "bold"),
                                 bg="#B0C4DE", width=16, height=3, relief="groove", bd=2)
            emoji_box.pack(side=tk.LEFT, padx=10)

            temp_box = tk.Label(summary_frame, text=f"Today's Temp\n{curr_temp_max:.1f}°F / {curr_temp_min:.1f}°F", font=("Arial", 14, "bold"),
                                 bg="#FFD700", width=16, height=3, relief="groove", bd=2)
            temp_box.pack(side=tk.LEFT, padx=10)

            precip_box = tk.Label(summary_frame, text=f"Precipitation\n{curr_precip:.0f}%", font=("Arial", 14, "bold"),
                                  bg="#87CEEB", width=16, height=3, relief="groove", bd=2)
            precip_box.pack(side=tk.LEFT, padx=10)

            wind_box = tk.Label(summary_frame, text=f"Wind Speed\n{curr_wind:.1f} mph", font=("Arial", 14, "bold"),
                                 bg="#B0C4DE", width=16, height=3, relief="groove", bd=2)
            wind_box.pack(side=tk.LEFT, padx=10)
            # --- End summary boxes ---

            dates = []
            temps = []
            descs = []
            temps_max = []  # Initialize temps_max
            temps_min = []  # Initialize temps_min

            for day_data in daily_forecasts:
                date_obj = datetime.fromtimestamp(day_data["dt"]).date()
                dates.append(date_obj.strftime("%Y-%m-%d"))
                
                # Use daily average temperature for the graph
                daily_avg_temp = (day_data["temp"]["max"] + day_data["temp"]["min"]) / 2
                temps.append(daily_avg_temp)
                
                description = day_data["weather"][0]["description"].capitalize()
                descs.append(description)
                print(f"Weather Description from API: {description}")  # Add this line
                
                temps_max.append(day_data["temp"]["max"]) # Append max temp
                temps_min.append(day_data["temp"]["min"]) # Append min temp

            chart_type = self.chart_type.get()

            try:
                plt.rcParams['font.family'] = ['Segoe UI Emoji', 'sans-serif']
            except:
                plt.rcParams['font.family'] = ['sans-serif']

            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor("#8baaed")
            ax.set_facecolor("#0154fb")
            for spine in ax.spines.values():
                spine.set_visible(False)
            if chart_type == "bar":
                bar_colors = [
                    OWM_WEATHER_EMOJIS.get(desc.lower(), ('❓', '#CCCCCC'))[1]
                    for desc in descs
                ]
                bars = ax.bar(range(len(dates)), temps_max, color=bar_colors)
                ax.set_ylabel("Max Temperature (°F)")
                ax.set_title(f"{num_forecast_days}-Day Forecast for {selected_city_name}", pad=20, fontsize=16, fontweight='bold')
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, rotation=45, ha='right')

                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    desc = descs[i] if i < len(descs) and isinstance(descs[i], str) else ''
                    emoji, _ = OWM_WEATHER_EMOJIS.get(desc.lower(), ('❓', "#FF0000"))
                    emoji_color_map = {
                        '☀️': "#FFE600", '🌤️': '#1E90FF', '⛅': '#4682B4', '☁️': '#808080',
                        '🌦️': '#00BFFF', '🌧️': '#4169E1', '⛈️': '#8B0000', '🌨️': '#A9A9A9',
                        '🌫️': '#A0522D', '❓': '#FF0000',
                        '🌩️': '#800080', '🌪️': '#696969', '🌬️': '#B0E0E6', '🌈': '#FF69B4',
                        '🔥': '#FF4500', '🧊': '#00CED1', '🌡️': '#DC143C', '💧': '#1E90FF',
                        '🌀': '#4682B4', '🌁': '#A9A9A9', '🌻': '#FFD700', '🌵': '#DEB887',
                        '🌲': '#228B22', '🌳': '#32CD32', '🌴': '#2E8B57', '🌾': '#F5DEB3',
                        '🌋': '#B22222', '🌕': '#FFFF00', '🌑': '#2F4F4F', '🌙': '#F0E68C',
                        '⭐': '#FFD700', '⚡': '#FFFF00', '❄️': '#B0E0E6', '☔': '#1E90FF',
                        '☃️': '#B0E0E6', '🛑': '#FF0000'
                    }
                    
                    color = emoji_color_map.get(emoji, '#FF0000')
                    ax.annotate(
                        emoji,
                        xy=(bar.get_x() + bar.get_width() / 1.3, height),
                        xytext=(0, 0), textcoords="offset points",
                        ha='center', va='bottom', fontsize=20, fontweight='bold',
                        color=color,
                    )
            elif chart_type == "line":
                ax.plot(dates, temps_max, marker='o', linestyle='-', color='red', label='Max Temp')
                ax.plot(dates, temps_min, marker='o', linestyle='-', color='yellow', label='Min Temp')
                ax.set_ylabel("Temperature (°F)")
                ax.set_title(f"{num_forecast_days}-Day Temperature Trend for {selected_city_name}", pad=20, fontsize=16, fontweight='bold')
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, rotation=45, ha='right')
                ax.legend()

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            tk.Label(self.graph_frame, text=f"Failed to fetch 14-day forecast for {selected_city_name}.", fg="red").pack()

        # --- Automatically Get Historical Data (Open-Meteo) ---
        hist_start_date = datetime(2024, 7, 1).date()
        hist_end_date = datetime.now().date()

        if hist_start_date > hist_end_date:
            print(f"Historical data fetch skipped for {selected_city_name}: start date ({hist_start_date}) is after end date ({hist_end_date}).")
            return

        hist_start_date_str = hist_start_date.isoformat()
        hist_end_date_str = hist_end_date.isoformat()

        print(f"Fetching historical data for {selected_city_name} "
              f"from {hist_start_date_str} to {hist_end_date_str} for CSV.")

        historical_weather_data = fetch_historical_daily_data(
            lat, lon, timezone, hist_start_date_str, hist_end_date_str
        )

        if historical_weather_data:
            create_historical_data_csv(
                selected_state_name, selected_city_name, historical_weather_data,
                hist_start_date_str, hist_end_date_str, self.STATE_CITY_DATA
            )
        else:
            messagebox.showwarning("Historical Data Save Failed",
                                   f"Could not fetch historical data for {selected_city_name} to save to CSV.")