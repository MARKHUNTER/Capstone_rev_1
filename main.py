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


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboardApp(root)

    def on_closing():
        """Handle application shutdown gracefully"""
        try:
            # Close all matplotlib figures to prevent hanging
            import matplotlib.pyplot as plt
            plt.close('all')
            
            # Destroy the main application
            if hasattr(app, 'cleanup'):
                app.cleanup()
            
            root.quit()  # Exit mainloop
            root.destroy()  # Destroy window
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            pass  # Ignore errors during shutdown
        finally:
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()