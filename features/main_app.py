# features/main_app.py
import tkinter as tk
import tkinter.ttk as ttk

# --- CRITICAL FIX: Ensure THESE TWO LINES are at the top and are correct ---
from features.forecast_tab import ForecastTab
from features.historical_tab import HistoricalTab
# --- END CRITICAL FIX ---

class WeatherDashboardApp:
    def __init__(self, master):
        # Set larger font for notebook tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold")) # This line sets the tab font size

        self.master = master
        master.title("Weather Dashboard & Historical Data")
        master.geometry("1000x800")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        # These lines require ForecastTab and HistoricalTab to be imported
        self.forecast_tab = ForecastTab(self.notebook, master) # This line now finds ForecastTab
        self.historical_tab = HistoricalTab(self.notebook, master) # This line now finds HistoricalTab

        self.notebook.add(self.forecast_tab, text="7-Day Forecast")
        self.notebook.add(self.historical_tab, text="Monthly Averages")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboardApp(root)
    root.mainloop()