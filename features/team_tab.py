import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict

class TeamTab(ttk.Frame):
    def __init__(self, parent_notebook):
        super().__init__(parent_notebook)
        self.parent_notebook = parent_notebook
        self.team_data = None
        self.chart_data = {}
        self.chart_widgets = {}
        self.selected_cities = []  # List of selected cities
        self.city_vars = {}  # Dict of city:tk.BooleanVar
        self.selected_variable = tk.StringVar(value="max_temp")
        self.chart_type = tk.StringVar(value="monthly")

        self.load_team_data()
        self.create_widgets()

    def load_team_data(self):
        csv_filepath = os.path.join("GroupData", "team_weather_data.csv")
        try:
            self.team_data = pd.read_csv(csv_filepath)
            self.team_data['date'] = pd.to_datetime(self.team_data['date'])
        except FileNotFoundError:
            messagebox.showerror("Error", "team_weather_data.csv not found!")
            self.team_data = None

    def create_widgets(self):
        header_label = tk.Label(self, text="Team Weather Data", font=("Arial", 20, "bold"), bg="#8baaed")
        header_label.pack(fill=tk.X, pady=10)



        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=5, fill="x")

        # --- City Selection (Checkboxes) in a LabelFrame ---
        city_lf = tk.LabelFrame(self.input_frame, text="Select Cities", font=("Arial", 11, "bold"), padx=6, pady=2)
        city_lf.grid(row=0, column=0, sticky="w", padx=5, pady=(0, 2))
        cities = sorted(self.team_data['city'].unique().tolist()) if self.team_data is not None else []
        city_frame = tk.Frame(city_lf)
        city_frame.pack(anchor="w")
        self.city_vars = {}
        # Place checkboxes in a grid, 3 per row for compactness
        for i, city in enumerate(cities):
            var = tk.BooleanVar(value=False)
            self.city_vars[city] = var
            cb = tk.Checkbutton(city_frame, text=city, variable=var, font=("Arial", 10), command=self._update_selected_cities)
            cb.grid(row=i//3, column=i%3, sticky='w', padx=(0, 8), pady=(0, 2))
        # Select all by default
        for var in self.city_vars.values():
            var.set(True)
        self._update_selected_cities()

        # --- Variable Selection (Radio Buttons) in a LabelFrame, next to cities ---
        variables = {"Max Temp": "max_temp", "Min Temp": "min_temp", "Precipitation": "precip", "Wind Speed": "max_wind_spd"}
        variable_lf = tk.LabelFrame(self.input_frame, text="Variable", font=("Arial", 11, "bold"), padx=6, pady=2)
        variable_lf.grid(row=0, column=1, sticky="w", padx=5, pady=(0, 2))
        variable_frame = tk.Frame(variable_lf)
        variable_frame.pack(anchor="w")
        for idx, (text, var) in enumerate(variables.items()):
            rb = tk.Radiobutton(variable_frame, text=text, variable=self.selected_variable, value=var, font=("Arial", 10))
            rb.grid(row=idx//2, column=idx%2, sticky="w", padx=(0, 6), pady=(0, 2))

        # --- Chart Type Selection (Radio Buttons) in a LabelFrame, next to variable ---
        chart_type_lf = tk.LabelFrame(self.input_frame, text="Chart Type", font=("Arial", 11, "bold"), padx=6, pady=2)
        chart_type_lf.grid(row=0, column=2, sticky="w", padx=5, pady=(0, 2))
        chart_type_frame = tk.Frame(chart_type_lf)
        chart_type_frame.pack(anchor="w")
        tk.Radiobutton(chart_type_frame, text="Monthly", variable=self.chart_type, value="monthly", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Radiobutton(chart_type_frame, text="Daily", variable=self.chart_type, value="daily", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 6))


        # --- Chart Frame ---
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(pady=10, fill="both", expand=True)

        # --- Bind all controls to auto-generate chart on change ---
        def bind_update(widget):
            widget.config(command=self._on_selection_change)

        # Bind city checkboxes
        for cb in city_frame.winfo_children():
            bind_update(cb)
        # Bind variable radio buttons
        for rb in variable_frame.winfo_children():
            bind_update(rb)
        # Bind chart type radio buttons
        for rb in chart_type_frame.winfo_children():
            bind_update(rb)

        # Initial chart
        self.plot_team_chart()

    def _update_selected_cities(self):
        self.selected_cities = [city for city, var in self.city_vars.items() if var.get()]

    def _on_selection_change(self):
        self._update_selected_cities()
        self.plot_team_chart()

    def plot_team_chart(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if self.team_data is None:
            tk.Label(self.graph_frame, text="Data not loaded!", fg="red").pack()
            return

        selected_cities = self.selected_cities
        variable = self.selected_variable.get()
        chart_type = self.chart_type.get()

        if not selected_cities:
            tk.Label(self.graph_frame, text="No cities selected!", fg="red").pack()
            return

        filtered_data = self.team_data[self.team_data['city'].isin(selected_cities)]

        if filtered_data.empty:
            tk.Label(self.graph_frame, text="No data for selected cities!", fg="red").pack()
            return

        if chart_type == "monthly":
            self.plot_monthly_average_chart(filtered_data, variable)
        else:
            self.plot_daily_chart(filtered_data, variable)

    def plot_monthly_average_chart(self, data, variable):
        # Plot a grouped bar chart (one bar per city per month for selected cities)
        fig, ax = plt.subplots(figsize=(12, 6))
        data = data.copy()
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        grouped = data.groupby(['year', 'month', 'city'])[variable].mean().reset_index()
        grouped['plot_date'] = pd.to_datetime(grouped['year'].astype(str) + '-' + grouped['month'].astype(str).str.zfill(2) + '-01')
        # Pivot so each city is a column
        pivot = grouped.pivot(index='plot_date', columns='city', values=variable)
        cities = pivot.columns.tolist()
        x = range(len(pivot.index))
        total_width = 0.8
        bar_width = total_width / len(cities) if cities else total_width
        for i, city in enumerate(cities):
            offsets = [xi + (i - len(cities)/2)*bar_width + bar_width/2 for xi in x]
            ax.bar(offsets, pivot[city], width=bar_width, label=city)
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%Y-%m') for d in pivot.index], rotation=45)

        ax.set_xlabel("Month")
        ax.set_ylabel(variable)
        ax.set_title(f"Monthly Average {variable}")
        ax.legend(title="City")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def plot_daily_chart(self, data, variable):
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

        selected_cities = self.selected_cities
        if len(selected_cities) > 1:
            # Prepare data for selected cities, sorted by date
            all_dates = sorted(data['date'].unique())
            self.chart_data['all_dates'] = all_dates
            self.chart_data['all_cities'] = selected_cities
            self.chart_data['data'] = data

            num_dates = len(all_dates)
            slider = ttk.Scale(
                container,
                orient='horizontal',
                from_=0,
                to=max(0, num_dates - 14),
                command=self._update_all_cities_daily_chart_view
            )
            slider.pack(fill='x', pady=(5,0))
            self._update_all_cities_daily_chart_view(0)
        else:
            self.chart_data['dates'] = data['date'].tolist()
            self.chart_data['temps'] = data[variable].tolist()
            self.chart_data['city_name'] = selected_cities[0] if selected_cities else ""

            num_dates = len(self.chart_data['dates'])
            slider = ttk.Scale(
                container,
                orient='horizontal',
                from_=0,
                to=max(0, num_dates - 14),
                command=self._update_daily_chart_view
            )
            slider.pack(fill='x', pady=(5,0)) # Add some padding
            # Initial plot draw
            self._update_daily_chart_view(0)

    def _update_all_cities_daily_chart_view(self, scroll_value):
        start_index = int(float(scroll_value))
        all_dates = self.chart_data['all_dates']
        cities = self.chart_data['all_cities']
        data = self.chart_data['data']
        ax = self.chart_widgets['ax']
        canvas = self.chart_widgets['canvas']
        visible_points = 14
        end_index = start_index + visible_points
        visible_dates = all_dates[start_index:end_index]
        ax.cla()
        for city in cities:
            city_data = data[(data['city'] == city) & (data['date'].isin(visible_dates))]
            ax.plot(city_data['date'], city_data[self.selected_variable.get()], marker='o', label=city)
        ax.set_title(f"Daily {self.selected_variable.get()} for Selected Cities", pad=20)
        ax.set_ylabel(self.selected_variable.get())
        ax.tick_params(axis='x', rotation=45)
        ax.legend(title="City")
        canvas.draw()

    def _update_daily_chart_view(self, scroll_value):
        start_index = int(float(scroll_value))
        
        # Check if chart widgets are available
        if 'ax' not in self.chart_widgets or 'canvas' not in self.chart_widgets:
            print("Chart widgets not properly initialized.")
            return
        
        ax = self.chart_widgets['ax']
        canvas = self.chart_widgets['canvas']
        dates = self.chart_data['dates']
        temps = self.chart_data['temps']
        city_name = self.chart_data['city_name']
        
        visible_points = 14
        end_index = start_index + visible_points
        
        visible_dates = dates[start_index:end_index]
        visible_temps = temps[start_index:end_index]
        
        ax.cla()
        ax.plot(visible_dates, visible_temps, color='#007acc', marker='o', markersize=5)
        
        ax.set_title(f"Daily {self.selected_variable.get()} for {city_name}", pad=20)
        ax.set_ylabel(self.selected_variable.get())

        ax.tick_params(axis='x', rotation=45)
        
        canvas.draw()