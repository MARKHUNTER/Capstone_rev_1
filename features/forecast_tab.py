# features/forecast_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import os

# Import from local features package
from features.config import STATE_CITY_DATA, OWM_WEATHER_EMOJIS, emoji_font
from features.api import fetch_owm_forecast, fetch_historical_daily_data
from features.csv_files import create_historical_data_csv


class ForecastTab(ttk.Frame):
    def __init__(self, notebook, parent_root):
        super().__init__(notebook)
        self.parent_root = parent_root
        self.create_widgets()

    def create_widgets(self):
        # Header label for 7-Day Forecast
        header_label = tk.Label(self, text="7-Day Weather Forecast For Selected Cities", font=("Arial", 20, "bold"), bg="#c8c8f3")
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
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.city_var,
            state="readonly",
            font=("Arial", 14)
        )
        self.city_dropdown.pack(side=tk.LEFT, padx=5)

        self.state_dropdown.bind("<<ComboboxSelected>>", self.update_cities_dropdown)
        self.update_cities_dropdown()

        style = ttk.Style()
        style.configure('Rounded.TButton',
            padding=6,
            relief="raised",
            foreground="#000000",
            background="#ADD8E6",
            font=('Arial', 12, 'bold')
        )
        # Button text for 7-Day Forecast
        get_btn = ttk.Button(dropdown_frame, text="Get Forecast", style='Rounded.TButton', width=15, command=self.get_weekly_forecast)
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
        selected_city_name = self.city_var.get()
        selected_state_name = self.state_var.get()

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

        # --- Fetch 7-Day Forecast (OpenWeatherMap) ---
        forecast_data = fetch_owm_forecast(lat, lon)

        if forecast_data:
            forecasts = forecast_data["list"]

            # --- Add current weather summary boxes ---
            current = forecasts[0]
            curr_temp = current["main"]["temp"]
            curr_precip = current.get("pop", 0) * 100
            curr_wind = current["wind"]["speed"]

            summary_frame = tk.Frame(self.graph_frame)
            summary_frame.pack(pady=10)

            temp_box = tk.Label(summary_frame, text=f"Current Temp\n{curr_temp:.1f}°F", font=("Arial", 14, "bold"),
                                 bg="#FFD700", width=16, height=3, relief="groove", bd=2)
            temp_box.pack(side=tk.LEFT, padx=10)

            precip_box = tk.Label(summary_frame, text=f"Precipitation\n{curr_precip:.0f}%", font=("Arial", 14, "bold"),
                                  bg="#87CEEB", width=16, height=3, relief="groove", bd=2)
            precip_box.pack(side=tk.LEFT, padx=10)

            wind_box = tk.Label(summary_frame, text=f"Wind Speed\n{curr_wind:.1f} mph", font=("Arial", 14, "bold"),
                                 bg="#B0C4DE", width=16, height=3, relief="groove", bd=2)
            wind_box.pack(side=tk.LEFT, padx=10)
            # --- End summary boxes ---

            days = {}
            for entry in forecasts:
                date = entry["dt_txt"].split(" ")[0]
                if date not in days:
                    days[date] = {
                        "temp": entry["main"]["temp"],
                        "desc": entry["weather"][0]["description"]
                    }
                    if len(days) == 7:
                        break
            dates = list(days.keys())
            temps = [info["temp"] for info in days.values()]
            descs = [info["desc"].capitalize() for info in days.values()]

            bar_colors = [
                OWM_WEATHER_EMOJIS.get(desc.lower(), ('❓', '#CCCCCC'))[1]
                for desc in descs
            ]

            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor("#c8c8f3")
            ax.set_facecolor("#f3e7a3")
            for spine in ax.spines.values():
                spine.set_visible(False)
            bars = ax.bar(range(len(dates)), temps, color=bar_colors)
            ax.set_ylabel("Temperature (°F)")
            ax.set_title(f"{len(dates)}-Day Forecast for {selected_city_name}", pad=20)
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, ha='right')

            for bar, desc in zip(bars, descs):
                height = bar.get_height()
                emoji, _ = OWM_WEATHER_EMOJIS.get(desc.lower(), ('❓', '#CCCCCC'))
                emoji_color_map = {
                    '☀️': '#FFA500', '🌤️': '#1E90FF', '⛅': '#4682B4', '☁️': '#808080',
                    '🌦️': '#00BFFF', '🌧️': '#4169E1', '⛈️': '#8B0000', '🌨️': '#A9A9A9',
                    '🌫️': '#A0522D', '❓': '#FF0000'
                }
                color = emoji_color_map.get(emoji, '#FF0000')
                ax.annotate(
                    emoji,
                    xy=(bar.get_x() + bar.get_width() / 1.3, height),
                    xytext=(0, 0), textcoords="offset points",
                    ha='center', va='bottom', fontsize=30,
                    color=color,
                    fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None
                )

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            tk.Label(self.graph_frame, text=f"Failed to fetch 7-day forecast for {selected_city_name}.", fg="red").pack()


        # --- Automatically Get Historical Data (Open-Meteo) ---
        # Get historical data from July 1, 2024, to the present date
        hist_start_date = datetime(2024, 7, 1).date()
        hist_end_date = datetime.now().date() # Today's date

        if hist_start_date > hist_end_date:
            print(f"Historical data fetch skipped for {selected_city_name}: start date ({hist_start_date}) is after end date ({hist_end_date}).")
            return # Exit if the date range is invalid

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
                hist_start_date_str, hist_end_date_str
            )
        else:
            messagebox.showwarning("Historical Data Save Failed",
                                   f"Could not fetch historical data for {selected_city_name} to save to CSV.")