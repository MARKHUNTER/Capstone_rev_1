# Instructions for JTC Capstone Weather Application

## Tab Overview & Functionality

### Forecast Tab (`features/forecast_tab.py`)
- Provides a 7–14 day weather forecast for a selected city.
- **User Input: Dropdowns for state, city and number of days**
- After making selections, you must click the button to update the forecast display.
- Displays daily high/low temperatures and weather descriptions (with emoji) and a bar chart with a forecast showing the average daily temperature for selected city and number of days

### Historical Tab (`features/historical_tab.py`)
- Displays historical monthly average temperatures for a selected city.
- **User Input: Dropdowns for state and city and option button for chart type**
- After making a selection, you must click the button to update the chart.
- If a bar chart is selected then the bar chart will show the monthly averages temperatures and the chart title updates to reflect the data range.
- If the daily line chart is selected, the chart shows a line chart with the min, max and average dailyt temparature and a horizontal scrollbar appears below the chart. Use this scrollbar to scroll through the date range, viewing 14 days at a time. The chart title updates to show the currently visible date range.

### Team Tab (`features/team_tab.py`)
- Allows multi-city comparison of weather data (team/group data).
- **User Input: Checkboxes for city selection, radio buttons for variable selection, dropdown for chart type, grid layout**
- Supports both grouped bar charts (monthly) and multi-line charts (daily) for selected cities
 - When the daily line chart is selected, a horizontal scrollbar appears below the chart. Use this scrollbar to scroll through the date range, viewing 14 days at a time. The chart title updates to show the currently visible date range.
- All controls update the chart automatically (no button needed).



