# main.py
import sys
import os
import tkinter as tk
from dotenv import load_dotenv
import pandas as pd

# Add the 'features' folder to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
feature_path = os.path.join(project_root, "features")
if feature_path not in sys.path:
    sys.path.insert(0, feature_path) # Insert at beginning for priority

# Load environment variables
load_dotenv(os.path.join(project_root, ".env")) # Specify path to .env file

# Import the main application class
from features.main_app import WeatherDashboardApp
#from features.forecast_tab import ForecastTab

# Sample monthly data for testing
monthly_data = pd.DataFrame({
    'date': [202301, 202302, 202303],
    0: [30, 28, 35]
})

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboardApp(root)

    def on_closing():
        root.destroy()
       # sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()