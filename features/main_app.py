import tkinter as tk
import tkinter.ttk as ttk
from features.forecast_tab import ForecastTab
from features.historical_tab import HistoricalTab


class WeatherDashboardApp:
    def __init__(self, master):
        self.master = master
        master.title("Weather Dashboard & Historical Data")
        master.geometry("1000x800")

        style = ttk.Style()
        style.theme_use("clam")
        
        # --- Configure Notebook Tabs Styling ---
        # Set larger font for notebook tabs
        style.configure("TNotebook.Tab", font=("Arial", 14, "bold"), padding=(10, 5))

        # Default (unselected) tab background and foreground (text) color
        style.configure("TNotebook.Tab", background="#dcdad5", foreground="#b5b3ae")  # Light gray background, black text

        # Map colors for different tab states
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", "#091746"),  # Light blue when selected
                ("active", "#8baaed"),    # Light Cyan when hovered over (active)
            ],
            foreground=[
                ("selected", "#8baaed"),    # Black text when selected
                ("active", "#091746"),      # Black text when hovered over
            ]
        )
        # --- End Notebook Tabs Styling ---

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.forecast_tab = ForecastTab(self.notebook)
        self.historical_tab = HistoricalTab(self.notebook)

        self.notebook.add(self.forecast_tab, text=" 7-Day Forecast ")
        self.notebook.add(self.historical_tab, text=" Monthly Averages ")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboardApp(root)
    root.mainloop()