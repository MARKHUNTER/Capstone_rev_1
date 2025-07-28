
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import csv
import os

from features.config import STATE_CITY_DATA
from features.api import fetch_historical_daily_data
from features.csv_files import HISTORY_DIR, create_historical_data_csv


class HistoricalTab(ttk.Frame):
    def __init__(self, parent_notebook):
        super().__init__(parent_notebook)
        self.parent_notebook = parent_notebook
        self.chart_data = {}
        self.chart_widgets = {}
        
        self.create_widgets()

    def create_widgets(self):
        header_label = tk.Label(self, text="Historical Average Temperatures", font=("Arial", 20, "bold"), bg="#8baaed")
        header_label.pack(fill=tk.X, pady=10)

        dropdown_frame = tk.Frame(self)
        dropdown_frame.pack(pady=5)

        tk.Label(
            dropdown_frame,
            text="Select State:",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
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
            textvariable=self.city_var,
            values=[],
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
        self.get_chart_btn = ttk.Button(dropdown_frame, text="Get Averages Chart", style='Rounded.TButton', width=20, command=self.get_average_chart)
        self.get_chart_btn.pack(side=tk.LEFT, padx=10)

        self.chart_type = tk.StringVar(value="monthly")
        chart_type_frame = tk.Frame(dropdown_frame)
        chart_type_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(chart_type_frame, text="Chart Type:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Radiobutton(chart_type_frame, text="Monthly", variable=self.chart_type, value="monthly", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Radiobutton(chart_type_frame, text="Daily", variable=self.chart_type, value="daily", font=("Arial", 12)).pack(side=tk.LEFT)

        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(pady=10, fill="both", expand=True)

        self.status_label = ttk.Label(self, text="Ready.")
        self.status_label.pack(pady=5)

        # Bind the window close event
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """This function is called when the window is closed."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Destroy the Matplotlib figures
            for fig in [self.chart_widgets.get('fig'), getattr(self, 'fig', None)]:
                if fig:
                    plt.close(fig)

            # Destroy the main window
            self.winfo_toplevel().destroy()

    def update_cities_dropdown(self, event=None):
        selected_state = self.state_var.get()
        cities_in_state = sorted(list(STATE_CITY_DATA.get(selected_state, {}).keys()))
        self.city_dropdown['values'] = cities_in_state
        if cities_in_state:
            self.city_var.set(cities_in_state[0])
        else:
            self.city_var.set("")

    def get_average_chart(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Ensure charts are closed before creating new ones
        if 'fig' in self.chart_widgets and self.chart_widgets['fig'] is not None:
            plt.close(self.chart_widgets['fig'])
        
        self.chart_data = {}
        self.chart_widgets = {}

        selected_state_name = self.state_var.get()
        selected_city_name = self.city_var.get()

        self.status_label.config(text="Processing...")
        self.get_chart_btn.config(state=tk.DISABLED)
        self.winfo_toplevel().update_idletasks()

        if not selected_city_name:
            messagebox.showwarning("Selection Error", "Please select a city.")
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        city_info = STATE_CITY_DATA.get(selected_state_name, {}).get(selected_city_name)
        if not city_info:
            messagebox.showerror("Error", "City data not found.")
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        lat = city_info["lat"]
        lon = city_info["lon"]
        timezone = city_info["timezone"]

        filename = f"{selected_state_name.replace(' ', '_').lower()}_{selected_city_name.replace(' ', '_').lower()}_daily_weather_history.csv"
        csv_filepath = os.path.join(HISTORY_DIR, filename)

        all_daily_data = []

        if not os.path.exists(csv_filepath) or os.path.getsize(csv_filepath) == 0:
            messagebox.showinfo("Data Not Found", f"Historical data file not found for {selected_city_name}. Fetching data now...")
            self.status_label.config(text=f"Fetching historical data for {selected_city_name}...")
            self.winfo_toplevel().update_idletasks()
            
            # Using current date - 1 year to current date - 1 day
            # Current date is July 28, 2025
            import_start_date = datetime(2024, 7, 27).date() # One year before July 28, 2025
            import_end_date = datetime.now().date() - timedelta(days=1)

            if import_start_date > import_end_date:
                messagebox.showwarning("Date Error", "The historical start date is after the end date. No data to fetch.")
                self.status_label.config(text="Ready.")
                self.get_chart_btn.config(state=tk.NORMAL)
                return

            import_start_date_str = import_start_date.isoformat()
            import_end_date_str = import_end_date.isoformat()

            historical_weather_data = fetch_historical_daily_data(lat, lon, timezone, import_start_date_str, import_end_date_str)

            if historical_weather_data and 'daily' in historical_weather_data:
                create_historical_data_csv(selected_state_name, selected_city_name, historical_weather_data, import_start_date_str, import_end_date_str, STATE_CITY_DATA)
            else:
                messagebox.showwarning("Import Failed", f"Could not fetch historical data for {selected_city_name}.")
                self.status_label.config(text="Ready.")
                self.get_chart_btn.config(state=tk.NORMAL)
                return
        
        try:
            with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    all_daily_data.append(row)
        except Exception as e:
            messagebox.showerror("File Read Error", f"Failed to read data file: {e}")
            self.status_label.config(text="Ready.")
            self.get_chart_btn.config(state=tk.NORMAL)
            return

        chart_type = self.chart_type.get()

        if chart_type == "monthly":
            self.plot_monthly_chart(all_daily_data, selected_city_name)
        elif chart_type == "daily":
            self.plot_daily_chart(all_daily_data, selected_city_name)
        else:
            tk.Label(self.graph_frame, text="Invalid chart type selected.", fg="red").pack()
        
        self.status_label.config(text=f"Displaying historical data for {selected_city_name}")
        self.get_chart_btn.config(state=tk.NORMAL)

    def plot_monthly_chart(self, all_daily_data, selected_city_name):
        if not all_daily_data:
            tk.Label(self.graph_frame, text="No historical data to calculate monthly averages.", fg="red").pack()
            return

        monthly_temps_sum = defaultdict(float)
        monthly_temps_count = defaultdict(int)
        min_date_loaded, max_date_loaded = datetime.max.date(), datetime.min.date()

        for row in all_daily_data:
            try:
                date_obj = datetime.fromisoformat(row.get('Date')).date()
                max_temp = float(row.get('Max Temperature (°F)'))
                min_temp = float(row.get('Min Temperature (°F)'))
            except (ValueError, TypeError, AttributeError):
                continue

            min_date_loaded = min(min_date_loaded, date_obj)
            max_date_loaded = max(max_date_loaded, date_obj)
            month_year = date_obj.strftime("%Y-%m")
            daily_avg_temp = (max_temp + min_temp) / 2
            monthly_temps_sum[month_year] += daily_avg_temp
            monthly_temps_count[month_year] += 1

        monthly_averages = {my: monthly_temps_sum[my] / monthly_temps_count[my] for my in sorted(monthly_temps_sum) if monthly_temps_count[my] > 0}

        if not monthly_averages:
            tk.Label(self.graph_frame, text="No valid data to calculate monthly averages.", fg="red").pack()
            return

        months = list(monthly_averages.keys())
        avg_temps = list(monthly_averages.values())

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor("#c8c8f3")
        ax.set_facecolor("#f3e7a3")
        
        bars = ax.bar(months, avg_temps, color='#ADD8E6')
        ax.set_ylabel("Average Temperature (°F)")
        title_start_date = min_date_loaded.strftime("%b %Y")
        title_end_date = max_date_loaded.strftime("%b %Y")
        ax.set_title(f"Monthly Average Temperatures for {selected_city_name}\n(Data from {title_start_date} to {title_end_date})", pad=20)
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=60, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        for spine in ax.spines.values():
            spine.set_visible(False)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.5, round(yval, 1), ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _update_daily_chart_view(self, scroll_value):
        start_index = int(float(scroll_value))
        
        # Check if chart widgets are available and the line object exists
        if 'ax' not in self.chart_widgets or 'canvas' not in self.chart_widgets or 'line' not in self.chart_widgets or 'min_line' not in self.chart_widgets or 'max_line' not in self.chart_widgets:
            # print("Chart widgets not properly initialized.")
            return # Don't print, it can spam if user interacts before chart is ready
        
        ax = self.chart_widgets['ax']
        canvas = self.chart_widgets['canvas']
        line = self.chart_widgets['line'] # Get the average temperature line object
        min_line = self.chart_widgets['min_line']  # Get the min temperature line object
        max_line = self.chart_widgets['max_line']  # Get the max temperature line object
        dates = self.chart_data['dates']
        min_temps = self.chart_data['min_temps']
        max_temps = self.chart_data['max_temps']
        avg_temps = self.chart_data['temps']
        city_name = self.chart_data['city_name']
        y_limits = self.chart_data['y_limits']
        
        visible_points = 14
        end_index = start_index + visible_points
        
        visible_dates = dates[start_index:end_index]
        visible_min_temps = min_temps[start_index:end_index]
        visible_max_temps = max_temps[start_index:end_index]
        visible_avg_temps = avg_temps[start_index:end_index]
        
        # Update data of the existing lines
        line.set_data(visible_dates, visible_avg_temps)
        min_line.set_data(visible_dates, visible_min_temps)
        max_line.set_data(visible_dates, visible_max_temps)
        
        # Update x-axis limits and ticks
        ax.set_xlim(visible_dates[0], visible_dates[-1])
        ax.set_xticks(visible_dates)
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in visible_dates], rotation=45, ha='right')
        
        # Keep y-axis limits consistent
        ax.set_ylim(y_limits)
        
        # Update title (if it contains dynamic date range for daily view)
        ax.set_title(f"Daily Temperatures for {city_name}\n({visible_dates[0].strftime('%b %d, %Y')} to {visible_dates[-1].strftime('%b %d, %Y')})", pad=20)
        
        # Redraw only the canvas
        canvas.draw()

    def plot_daily_chart(self, all_daily_data, selected_city_name):
        if not all_daily_data:
            tk.Label(self.graph_frame, text="No historical data for daily chart.", fg="red").pack()
            return

        daily_data = []
        # Filter data to include only the last 365 days from the latest available date
        # First, find the latest date in all_daily_data
        latest_date = None
        for row in all_daily_data:
            try:
                date_obj = datetime.fromisoformat(row.get('Date')).date()
                if latest_date is None or date_obj > latest_date:
                    latest_date = date_obj
            except (ValueError, TypeError, AttributeError):
                continue
        
        if latest_date:
            # Calculate the start date for the last 365 days relative to the latest date
            start_date_365_days_ago = latest_date - timedelta(days=364) # inclusive of latest date
            
            for row in all_daily_data:
                try:
                    date_obj = datetime.fromisoformat(row.get('Date')).date()
                    max_temp = float(row.get('Max Temperature (°F)'))
                    min_temp = float(row.get('Min Temperature (°F)'))
                    daily_avg_temp = (max_temp + min_temp) / 2
                    
                    if date_obj >= start_date_365_days_ago and date_obj <= latest_date:
                        daily_data.append((date_obj, daily_avg_temp, min_temp, max_temp))
                except (ValueError, TypeError, AttributeError):
                    continue
        
        if not daily_data:
            tk.Label(self.graph_frame, text="No valid daily data to display.", fg="red").pack()
            return
            
        daily_data = sorted(daily_data, key=lambda item: item[0])
        self.chart_data['dates'] = [item[0] for item in daily_data]
        self.chart_data['temps'] = [item[1] for item in daily_data]
        self.chart_data['min_temps'] = [item[2] for item in daily_data]
        self.chart_data['max_temps'] = [item[3] for item in daily_data]
        self.chart_data['city_name'] = selected_city_name

        padding = 5
        global_min_temp = min(self.chart_data['min_temps']) - padding
        global_max_temp = max(self.chart_data['max_temps']) + padding
        self.chart_data['y_limits'] = (global_min_temp, global_max_temp)

        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor("#c8c8f3")
        ax.set_facecolor("#f3e7a3")

        self.chart_widgets['fig'] = fig
        self.chart_widgets['ax'] = ax

        container = ttk.Frame(self.graph_frame)
        container.pack(fill="both", expand=True, pady=10, padx=10)
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.chart_widgets['canvas'] = canvas
        
        # Plot the initial lines and store their references
        line, = ax.plot([], [], color='#007acc', marker='o', markersize=5, label='Average')
        min_line, = ax.plot([], [], color='blue', linestyle='--', linewidth=1, label='Min')
        max_line, = ax.plot([], [], color='red', linestyle='--', linewidth=1, label='Max')
        self.chart_widgets['line'] = line
        self.chart_widgets['min_line'] = min_line
        self.chart_widgets['max_line'] = max_line
        
        ax.legend()
        
        num_dates = len(self.chart_data['dates'])
        slider = ttk.Scale(
            container,
            orient='horizontal',
            from_=0,
            to=max(0, num_dates - 14), # Ensure 'to' is not negative
            command=self._update_daily_chart_view
        )
        slider.pack(fill='x', pady=(5,0)) # Add some padding
        
        # Initial plot draw
        # Use a small delay with after to ensure all widgets are mapped before drawing
        self.after(10, lambda: self._update_daily_chart_view(slider.get()))
        
        # IMPORTANT: Do not plt.close(fig) here. The figure needs to remain open
        # for FigureCanvasTkAgg to continue displaying it and for updates to work.
        # The closing is handled in on_closing.