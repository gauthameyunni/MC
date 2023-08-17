#!/usr/bin/env python
# coding: utf-8

# In[ ]:



# Necessary Libraries
import flet as ft
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from datetime import datetime
import matplotlib
from flet.matplotlib_chart import MatplotlibChart
import matplotlib.dates as mdates
from flet import LineChart, BarChart

matplotlib.use("svg")


# Custom Formatter for Date Format in Plot
class MyFormatter(mdates.DateFormatter):
    def __init__(self):
        super().__init__('%b %d')

    def __call__(self, x, pos=0):
        if mdates.num2date(x).month == 1 and mdates.num2date(x).day < 7:
            return '{:%b %d, %Y}'.format(mdates.num2date(x))
        else:
            return '{:%b %d}'.format(mdates.num2date(x))

def calculate_forecast_table(results, start_date):
    # Define the probability intervals
    probabilities = np.arange(0, 101, 5)
    
    # Calculate the elapsed time for each probability interval
    elapsed_times = np.percentile(results, probabilities).round(1)
    # Calculate the completion dates for each elapsed time
    completion_dates = [(pd.Timestamp(start_date) + pd.Timedelta(days=time)).date() for time in elapsed_times]
    
    # Calculate the cost of delay
    cost_of_delay = np.round([time * 5230 for time in elapsed_times], 2)
    
    # Create a DataFrame to hold the results
    forecast_table = pd.DataFrame({
        'Probability (%)': probabilities[::-1],  # Reversed for descending order
        'Elapsed Time (Days)': elapsed_times[::-1],  # Reversed for descending order
        'Completion Date': completion_dates[::-1],  # Reversed for descending order
        'Cost of Delay': cost_of_delay[::-1]  # Reversed for descending order
    })

    return forecast_table

# Monte Carlo simulation function
def monte_carlo_simulation(throughput_data, leadtime_data, backlog_items, focus, num_simulations):
    """Run the Monte Carlo simulation."""
    # Convert the throughput and lead time data to numpy arrays
    throughput_data = throughput_data['Throughput'].values
    leadtime_data = leadtime_data['Leadtime'].values

    # Initialize an array to store the results
    results = np.zeros(num_simulations)

    # Run the simulations
    for i in range(num_simulations):
        # Initialize variables for the number of items completed and the time elapsed
        items_completed = 0
        time_elapsed = 0

        # Continue until the backlog is completed
        while items_completed < backlog_items:
            # Generate random samples of throughput and lead time
            throughput_sample = np.random.choice(throughput_data)
            leadtime_sample = np.random.choice(leadtime_data)

            # Adjust the throughput based on the focus
            adjusted_throughput = throughput_sample * (focus / 100)

            # Add the adjusted throughput to the number of items completed
            items_completed += adjusted_throughput

            # Add the lead time to the time elapsed
            time_elapsed += leadtime_sample

        # Store the result (the time elapsed when the backlog is completed)
        results[i] = time_elapsed

    # Return the results
    return results

def monte_carlo_simulation_sp(sp_series, backlog_items, focus, num_simulations):
    
    # Similar to the throughput/leadtime-based simulation, but adapted for story points
    results = np.zeros(num_simulations)
    for i in range(num_simulations):
        total_sp = 0
        while total_sp < backlog_items:
            sp_sample = np.random.choice(sp_series.dropna())  # Sample from the series and drop NaN values
            adjusted_sp = sp_sample * (focus / 100)

            total_sp += adjusted_sp
        results[i] = total_sp
    return results

def main(page: ft.Page):
        # Yellow page theme with SYSTEM (default) mode
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.INDIGO,
    )
    page.theme_mode = ft.ThemeMode.DARK 
    page.bgcolor = ft.colors.SURFACE_VARIANT

    app = MonteCarloSimApp(page)
    page.title = "Monte Carlo Simulation"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(app.vlayout)

class MonteCarloSimApp(ft.UserControl):
    def initialize_tabs(self):
        # Create a container for the forecast table
        self.forecast_table_container = ft.Column()
        # Add the forecast table to the container
        self.forecast_table_container.controls.append(self.forecast_table)
        # In your initialize_tabs function
        self.figure1 = Figure()  # For plot_image
        self.plot_image = MatplotlibChart(self.figure1, expand=True)

        # Tab 1: Throughput Leadtime
        self.tab1_controls = ft.Column(
            controls=[
                ft.Row(controls=[self.num_simulations, self.backlog_length, self.focus_percent, self.start_date], scroll=True),
                ft.Row(controls=[self.select_throughput_btn, self.select_leadtimes_btn, self.run_simulation_btn], scroll=True),
                ft.Row(controls=[self.download_table_button, self.download_insights_button, self.download_plot_button], scroll=True),
                ft.Row(controls=[self.forecast_table_container, self.plot_image]),
                self.trend_insight_label, 
                self.volatility_insight_label, 
            ],
           # scroll=True,
            expand=True,
            spacing=10 # Adding spacing between rows
        )

        # Tab 2: Story Points
        self.forecast_table_container_sp = ft.Column()
        self.forecast_table_container_sp.controls.append(self.forecast_table_sp)

        self.figure2 = Figure()  # For plot_image_sp
        self.plot_image_sp = MatplotlibChart(self.figure2, expand=True)

        self.tab2_controls = ft.Column(
            controls=[
                ft.Row(controls=[self.num_simulations_sp, self.backlog_length_sp, self.focus_percent_sp, self.start_date_sp], scroll=True),
                ft.Row(controls=[self.select_story_point_btn, self.run_simulation_btn_sp], scroll=True),
                ft.Row(controls=[self.download_table_button_sp, self.download_insights_button_sp, self.download_plot_button_sp], scroll=True),
                ft.Row(controls=[self.forecast_table_container_sp, self.plot_image_sp]),
                self.trend_insight_label_sp, 
                self.volatility_insight_label_sp,
            ],
            expand=True,
            spacing=10
        )

        # Create tabs with the two columns
        self.tabs = ft.Tabs(
            tabs=[
                ft.Tab(text="Throughput/Leadtime", content=self.tab1_controls),  # Replace control_column with hlayout

                ft.Tab(text="Story Points", content=self.tab2_controls)
            ]
        )

        # Add the tabs to the vertical layout
        self.vlayout.controls.insert(0, self.tabs)

    def __init__(self, page):
        super().__init__()
        self.page = page

        # Vertical layout with scroll enabled
        self.vlayout = ft.Column(scroll=ft.ScrollMode.ALWAYS,expand=True)

        # Input fields
        self.num_simulations = ft.TextField(label="Number of Simulations")
        self.backlog_length = ft.TextField(label="Backlog Length")
        self.focus_percent = ft.TextField(label="Focus %")
        self.error_label = ft.Text("")  # Error label

        # Replace DatePicker with TextField
        self.start_date = ft.TextField(label="Start Forecast Date (YYYY-MM-DD)")

        # Buttons
        self.select_throughput_btn = ft.ElevatedButton("Select Throughput CSV")
        self.select_leadtimes_btn = ft.ElevatedButton("Select Lead Times CSV")
        self.run_simulation_btn = ft.ElevatedButton("Run Simulation")

        # Create file pickers for throughput and lead times
        self.throughput_file_picker = ft.FilePicker()
        self.leadtimes_file_picker = ft.FilePicker()

        # Define callback functions to handle file selection results
        def throughput_file_result(e: ft.FilePickerResultEvent):
            if e.files:
                self.throughput_file = e.files[0].path
                print("Throughput file selected:", self.throughput_file)

        def leadtimes_file_result(e: ft.FilePickerResultEvent):
            if e.files:
                self.leadtimes_file = e.files[0].path
                print("Leadtimes file selected:", self.leadtimes_file)

        self.throughput_file_picker.on_result = throughput_file_result
        self.leadtimes_file_picker.on_result = leadtimes_file_result

        # Add file pickers to page overlay
        self.page.overlay.extend([self.throughput_file_picker, self.leadtimes_file_picker])

        # Set on_click handlers for the buttons
        self.select_throughput_btn.on_click = lambda _: self.throughput_file_picker.pick_files(allowed_extensions=['csv','xlsx'])
        self.select_leadtimes_btn.on_click = lambda _: self.leadtimes_file_picker.pick_files(allowed_extensions=['csv','xlsx'])
        self.run_simulation_btn.on_click = self.run_simulation

        # Input fields
        self.num_simulations_sp = ft.TextField(label="Number of Simulations")
        self.backlog_length_sp = ft.TextField(label="Backlog Length")
        self.focus_percent_sp = ft.TextField(label="Focus %")
        self.error_label_sp = ft.Text("")  # Error label

        # Replace DatePicker with TextField
        self.start_date_sp = ft.TextField(label="Start Forecast Date (YYYY-MM-DD)")

        # Initialize the forecast table with an empty DataTable
        self.forecast_table = self.create_forecast_table(pd.DataFrame())

        # Insights labels
        self.trend_insight_label = ft.Text("")
        self.volatility_insight_label = ft.Text("")


        # Create file pickers for saving files
        table_file_picker = ft.FilePicker()
        insights_file_picker = ft.FilePicker()
        plot_file_picker = ft.FilePicker()

        # Create file pickers for saving files for SP
        table_file_picker_sp = ft.FilePicker()
        insights_file_picker_sp = ft.FilePicker()
        plot_file_picker_sp = ft.FilePicker()

        # Add file pickers to page overlay
        self.page.overlay.extend([table_file_picker, insights_file_picker, plot_file_picker])
        # Add file pickers to page overlay SP
        self.page.overlay.extend([table_file_picker_sp, insights_file_picker_sp, plot_file_picker_sp])
        # Define result handlers for saving files
        def save_table_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.origin_table.to_csv(e.path, index=False)

        def save_insights_result(e: ft.FilePickerResultEvent):
            if e.path:
                insights_text = (
                    "Trends Analysis:\n" + self.trend_insight_label.value +
                    "\n\nVolatility Analysis:\n" + self.volatility_insight_label.value 
                )
                with open(e.path, 'w') as file:
                    file.write(insights_text)

        def save_plot_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.figure1.savefig(e.path)

        # Set result handlers
        table_file_picker.on_result = save_table_result
        insights_file_picker.on_result = save_insights_result
        plot_file_picker.on_result = save_plot_result

        # Create download buttons
        self.download_table_button = ft.ElevatedButton("Download Table", on_click=lambda _: table_file_picker.save_file(file_name="forecast_table.csv"))
        self.download_insights_button = ft.ElevatedButton("Download Insights", on_click=lambda _: insights_file_picker.save_file(file_name="insights.txt"))
        self.download_plot_button = ft.ElevatedButton("Download Plot", on_click=lambda _: plot_file_picker.save_file(file_name="plot.png"))

        self.origin_table = None

        # Define result handlers for saving files
        def save_table_result_sp(e: ft.FilePickerResultEvent):
            if e.path:
                self.origin_table_sp.to_csv(e.path, index=False)

        def save_insights_result_sp(e: ft.FilePickerResultEvent):
            if e.path:
                insights_text = (
                    "Trends Analysis:\n" + self.trend_insight_label_sp.value +
                    "\n\nVolatility Analysis:\n" + self.volatility_insight_label_sp.value 
                )
                with open(e.path, 'w') as file:
                    file.write(insights_text)

        def save_plot_result_sp(e: ft.FilePickerResultEvent):
            if e.path:
                self.figure2.savefig(e.path)

        # Set result handlers
        table_file_picker_sp.on_result = save_table_result_sp
        insights_file_picker_sp.on_result = save_insights_result_sp
        plot_file_picker_sp.on_result = save_plot_result_sp

        # Create download buttons
        self.download_table_button_sp = ft.ElevatedButton("Download Table", on_click=lambda _: table_file_picker_sp.save_file(file_name="forecast_table_sp.csv", allowed_extensions=['csv','xlsx']))
        self.download_insights_button_sp = ft.ElevatedButton("Download Insights", on_click=lambda _: insights_file_picker_sp.save_file(file_name="insights_sp.txt", allowed_extensions=['pdf', 'txt']))
        self.download_plot_button_sp = ft.ElevatedButton("Download Plot", on_click=lambda _: plot_file_picker_sp.save_file(file_name="plot_sp.png", allowed_extensions=['jpg', 'png']))
        
        self.origin_table_sp = None

        self.select_story_point_btn = ft.ElevatedButton("Select Story Point File")
        self.run_simulation_btn_sp = ft.ElevatedButton("Run Simulation SP")
        self.story_point_file_picker = ft.FilePicker()
        self.story_point_file_picker.on_result = self.story_point_file_result
        self.page.overlay.extend([self.story_point_file_picker])
        self.select_story_point_btn.on_click = lambda _: self.story_point_file_picker.pick_files(allowed_extensions=['csv', "xlsx"])
        self.run_simulation_btn_sp.on_click = self.run_simulation_sp
        #self.forecast_table = self.create_forecast_table(pd.DataFrame())
        self.forecast_table_sp = self.create_forecast_table(pd.DataFrame())
        self.trend_insight_label_sp = ft.Text("")
        self.volatility_insight_label_sp = ft.Text("")
        # # Initialize the tabs
        self.initialize_tabs()
        # Add the vertical layout to the page
        self.page.add(self.vlayout)

    def create_forecast_table(self, forecast_data):
        rows = []
        if not forecast_data.empty:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row["Probability (%)"]))),
                        ft.DataCell(ft.Text(str(row["Elapsed Time (Days)"]))),
                        ft.DataCell(ft.Text(str(row["Completion Date"]))),
                        ft.DataCell(ft.Text(str(row["Cost of Delay"])))
                    ]
                ) for index, row in forecast_data.iterrows()
            ]

        # Create the DataTable object using the rows
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Probability (%)")),
                ft.DataColumn(ft.Text("Elapsed Time (Days)")),
                ft.DataColumn(ft.Text("Completion Date")),
                ft.DataColumn(ft.Text("Cost of Delay"))
            ],
            rows=rows
        )

        return table  # Return the DataTable object directly

    def update_forecast_table(self, forecast_table_data):
        # Create a new table based on the forecast data
        new_table = self.create_forecast_table(forecast_table_data)

        # Clear the content of the container
        self.forecast_table_container.controls.clear()

        # Add the new table to the container
        self.forecast_table_container.controls.append(new_table)

        # Update the instance variable to point to the new table
        self.forecast_table = new_table

        self.page.update()

    def create_forecast_table_sp(self, forecast_data):
        rows = []
        if not forecast_data.empty:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row["Probability (%)"]))),
                        ft.DataCell(ft.Text(str(row["Elapsed Time (Days)"]))),
                        ft.DataCell(ft.Text(str(row["Completion Date"]))),
                        ft.DataCell(ft.Text(str(row["Cost of Delay"])))
                    ]
                ) for index, row in forecast_data.iterrows()
            ]

        # Create the DataTable object using the rows
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Probability (%)")),
                ft.DataColumn(ft.Text("Elapsed Time (Days)")),
                ft.DataColumn(ft.Text("Completion Date")),
                ft.DataColumn(ft.Text("Cost of Delay"))
            ],
            rows=rows
        )

        return table  # Return the DataTable object directly

    def update_forecast_table_sp(self, forecast_table_data):
        # Create a new table based on the forecast data
        new_table = self.create_forecast_table_sp(forecast_table_data)

        # Clear the content of the container
        self.forecast_table_container_sp.controls.clear()

        # Add the new table to the container
        self.forecast_table_container_sp.controls.append(new_table)

        # Update the instance variable to point to the new table
        self.forecast_table_sp = new_table

        self.page.update()

    def analyze_throughput_trend(self,throughput_data):
        # Calculate the moving average or fit a linear model
        trend = throughput_data['Throughput'].rolling(window=2).mean()  # 4-week moving average
        is_increasing = trend.iloc[-1] > trend.iloc[-2]

        insight = "Throughput is increasing over the last month." if is_increasing else "Throughput is decreasing over the last month."
        return insight
    def analyze_leadtime_trend(self,leadtimes_data):
        # Similar analysis for lead times
        trend = leadtimes_data['Leadtime'].rolling(window=2).mean()
        is_increasing = trend.iloc[-1] > trend.iloc[-2]

        insight = "Lead times are increasing over the last month." if is_increasing else "Lead times are decreasing over the last month."
        return insight
    def analyze_volatility(self,throughput_data, leadtimes_data):
        throughput_volatility = throughput_data['Throughput'].std()
        leadtime_volatility = leadtimes_data['Leadtime'].std()

        insight = f"Throughput volatility: {throughput_volatility:.2f}, Lead time volatility: {leadtime_volatility:.2f}."
        return insight



    def validate_inputs(self):
        # Check that all required fields have been filled in
        if not all([self.backlog_length.value, self.focus_percent.value, self.num_simulations.value, self.start_date.value]):
            return False, "Please fill in all fields."

        # Check that the number of simulations is a valid integer
        try:
            int(self.num_simulations.value)
        except ValueError:
            return False, "Number of simulations must be an integer."

        # Check that the backlog length and focus % are valid floats
        try:
            float(self.backlog_length.value)
            float(self.focus_percent.value)
        except ValueError:
            return False, "Backlog length and focus % must be numbers."

        # Check that the start date is in the correct format
        try:
            datetime.strptime(self.start_date.value, "%Y-%m-%d")
        except ValueError:
            return False, "Start Forecast Date must be in the format YYYY-MM-DD."

        # Check that the throughput and lead times files have been selected
        if not hasattr(self, 'throughput_file') or not hasattr(self, 'leadtimes_file'):
            return False, "Please select the throughput and lead times CSV files."

        # Check that the selected files are CSV files
        if not (self.throughput_file.endswith('.csv') and self.leadtimes_file.endswith('.csv')):
            return False, "Please select CSV files for throughput and lead times."

        return True, ""



    def close_dlg(self, e): # Added event parameter 
        self.page.dialog.open = False
        self.page.update()
    def run_simulation(self, e):
        # Validate the inputs
        valid, error_message = self.validate_inputs()
        if not valid:
            # Create an AlertDialog with the error message
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Input Error"),
                content=ft.Text(error_message),
                actions=[
                    ft.TextButton("OK", on_click=self.close_dlg) 
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # Set and open the dialog
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
            return
        # Convert the backlog length, focus %, and number of simulations to floats/integers
        backlog_items = float(self.backlog_length.value)
        focus = float(self.focus_percent.value)
        num_simulations = int(self.num_simulations.value)
        throughput_data = pd.read_csv(self.throughput_file)
        leadtimes_data = pd.read_csv(self.leadtimes_file)
        # Call the simulation function with the converted input data
        simulation_results = monte_carlo_simulation(throughput_data, leadtimes_data, backlog_items, focus, num_simulations)

        # Convert start date from string to date object
        start_date_str = self.start_date.value
        start_day = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Calculate the forecast table
        forecast_table = calculate_forecast_table(simulation_results, start_day)
        self.origin_table = forecast_table

        self.update_forecast_table(forecast_table)
        
        self.plot_results(forecast_table['Completion Date']) # Call the plot method
        
        # Update insights
        self.trend_insight_label.value = self.analyze_throughput_trend(throughput_data)
        self.volatility_insight_label.value = self.analyze_volatility(throughput_data, leadtimes_data)


        self.page.update()

    def story_point_file_result(self, e):
        if e.files:
            self.story_point_file = e.files[0].path

    def validate_inputs_sp(self):
        if not all([self.backlog_length_sp.value, self.focus_percent_sp.value, self.num_simulations_sp.value, self.start_date_sp.value]):
            return False, "Please fill in all fields."
        try:
            int(self.num_simulations_sp.value)
        except ValueError:
            return False, "Number of simulations must be an integer."
        try:
            float(self.backlog_length_sp.value)
            float(self.focus_percent_sp.value)
        except ValueError:
            return False, "Backlog length and focus % must be numbers."
        try:
            datetime.strptime(self.start_date_sp.value, "%Y-%m-%d")
        except ValueError:
            return False, "Start Forecast Date must be in the format YYYY-MM-DD."
        if not hasattr(self, 'story_point_file'):
            return False, "Please select the story point CSV file."
        if not (self.story_point_file.endswith('.xlsx') or self.story_point_file.endswith('.csv')) :

            return False, "Please select a CSV or Excel file for story points."
        return True, ""

    def read_story_points_data(self, file_path):
        # Read the Excel file and concatenate all sheets
        all_series = []
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name)
            # Check for required columns
            if "Story Points" not in df.columns:
                return None
            # Exclude the last entry (total sum)
            all_series.append(df["Story Points"].iloc[:-1])
            
        # Concatenate all Series
        combined_series = pd.concat(all_series, ignore_index=True)
        
        return combined_series

    def run_simulation_sp(self, e):
        valid, error_message = self.validate_inputs_sp()
        if not valid:
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Input Error"),
                content=ft.Text(error_message),
                actions=[
                    ft.TextButton("OK", on_click=self.close_dlg)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
            return
        backlog_items = float(self.backlog_length_sp.value)
        focus = float(self.focus_percent_sp.value)
        num_simulations = int(self.num_simulations_sp.value)
        if self.story_point_file.endswith('.csv'):
            story_points_data = pd.read_csv(self.story_point_file)
            if story_points_data is None:
                self.display_error_dialog("The selected Excel file does not contain the required 'Story Points' column.")
                return
        elif self.story_point_file.endswith('.xlsx'): 

            # Read the story points data from the selected Excel file
            story_points_data = self.read_story_points_data(self.story_point_file)                
            # Validate the data
            if story_points_data is None:
                self.display_error_dialog("The selected Excel file does not contain the required 'Story Points' column.")
                return

        simulation_results = monte_carlo_simulation_sp(story_points_data, backlog_items, focus, num_simulations)

        start_date_str = self.start_date_sp.value
        start_day = datetime.strptime(start_date_str, "%Y-%m-%d")
        forecast_table_sp = calculate_forecast_table(simulation_results, start_day)
        self.origin_table_sp = forecast_table_sp
        self.update_forecast_table_sp(forecast_table_sp)
        self.plot_results_sp(forecast_table_sp['Completion Date'])
        self.trend_insight_label_sp.value = self.analyze_story_point_trend_sp(story_points_data)
        self.volatility_insight_label_sp.value = self.analyze_volatility_sp(story_points_data)
        self.page.update()


    def analyze_story_point_trend_sp(self, story_point_data):
        trend = story_point_data.rolling(window=3).mean()
        is_increasing = trend.iloc[-1] > trend.iloc[-3]
        insight = "Story points are increasing over the last month." if is_increasing else "Story points are decreasing over the last month."
        return insight

    def analyze_volatility_sp(self, story_point_data):
        story_point_volatility = story_point_data.std()
        insight = f"Story point volatility: {story_point_volatility:.2f}."
        return insight


    def plot_results(self, completion_dates):
        # Clear the previous plot
        self.figure1.clear()
        self.plot = self.figure1.add_subplot(111)

        # Function to format y-values as percentages
        def to_percent(y, position):
            return '{:.2f} %'.format(y * 100)

        # Plot the histogram and multiply the y-values by 100
        self.plot.hist(completion_dates, bins='auto', density=True, label='Histogram', color='skyblue', edgecolor='black', alpha=0.7)
        self.plot.yaxis.set_major_formatter(FuncFormatter(to_percent)) # Format y-ticks as percentages
        self.plot.set_title("Histogram and CDF of Estimated Completion Times")
        self.plot.set_xlabel("Completion Day (iterations)")
        self.plot.set_ylabel("Likelihood %")

        # Set the custom formatter
        self.plot.xaxis.set_major_formatter(MyFormatter()) # 2 weeks (one sprint)

        # Create the ECDF (not multiplied by 100 yet)
        sorted_results = np.sort(completion_dates)
        ecdf = np.arange(1, len(sorted_results) + 1) / len(sorted_results)

        # Create a second y-axis for the ECDF
        plot2 = self.plot.twinx()

        # Plot the ECDF on the second y-axis
        plot2.plot(sorted_results, ecdf * 100, label='ECDF', color='orange') # Multiply ECDF by 100
        plot2.set_ylabel("Confidence %")

        # Set the y-ticks for the right y-axis (Confidence %), converting fractions to percentages
        y_ticks_right = np.linspace(0, 100, 5) # 5 ticks, adjust as needed

        plot2.set_yticks(y_ticks_right)
        plot2.set_yticklabels(['{:.0f} %'.format(tick) for tick in y_ticks_right])

        # Add a legend to each y-axis
        self.plot.legend(loc="upper left")
        plot2.legend(loc="upper right")
        # Adjust the margins
        self.figure1.subplots_adjust(right=0.85)  # Adjust the right margin
        self.figure1.subplots_adjust(left=0.15)  # Adjust the right margin

        # Adjust the date labels
        self.figure1.autofmt_xdate()

        # Redraw the Matplotlib figure
        new_plot_image = MatplotlibChart(self.figure1, expand=True)

        # Find the row control that contains the old plot image
        for control in self.tab1_controls.controls:
            if isinstance(control, ft.Row) and self.plot_image in control.controls:
                row_control = control
                break

        # Find the index of the old plot image in the row control
        plot_image_index = row_control.controls.index(self.plot_image)

        # Replace the old plot image with the new one in the row control
        row_control.controls[plot_image_index] = new_plot_image

        # Update the instance variable to point to the new plot image
        self.plot_image = new_plot_image

        self.page.update()
    
    def plot_results_sp(self, completion_dates):
        # Clear the previous plot
        self.figure2.clear()
        self.plot_sp = self.figure2.add_subplot(111)

        # Function to format y-values as percentages
        def to_percent(y, position):
            return '{:.2f} %'.format(y * 100)

        # Plot the histogram and multiply the y-values by 100
        self.plot_sp.hist(completion_dates, bins='auto', density=True, label='Histogram', color='skyblue', edgecolor='black', alpha=0.7)
        self.plot_sp.yaxis.set_major_formatter(FuncFormatter(to_percent)) # Format y-ticks as percentages
        self.plot_sp.set_title("Histogram and CDF of Estimated Completion Times")
        self.plot_sp.set_xlabel("Completion Day (iterations)")
        self.plot_sp.set_ylabel("Likelihood %")

        # Set the custom formatter
        self.plot_sp.xaxis.set_major_formatter(MyFormatter()) # 2 weeks (one sprint)

        # Create the ECDF (not multiplied by 100 yet)
        sorted_results = np.sort(completion_dates)
        ecdf = np.arange(1, len(sorted_results) + 1) / len(sorted_results)

        # Create a second y-axis for the ECDF
        plot3 = self.plot_sp.twinx()

        # Plot the ECDF on the second y-axis
        plot3.plot(sorted_results, ecdf * 100, label='ECDF', color='orange') # Multiply ECDF by 100
        plot3.set_ylabel("Confidence %")

        # Set the y-ticks for the right y-axis (Confidence %), converting fractions to percentages
        y_ticks_right = np.linspace(0, 100, 5) # 5 ticks, adjust as needed
    
        plot3.set_yticks(y_ticks_right)
        plot3.set_yticklabels(['{:.0f} %'.format(tick) for tick in y_ticks_right])

        # Add a legend to each y-axis
        self.plot_sp.legend(loc="upper left")
        plot3.legend(loc="upper right")
        # Adjust the margins
        self.figure2.subplots_adjust(right=0.85)  # Adjust the right margin
        self.figure2.subplots_adjust(left=0.15)  # Adjust the right margin

        # Adjust the date labels
        self.figure2.autofmt_xdate()
        
        # Redraw the Matplotlib figure
        new_plot_image = MatplotlibChart(self.figure2, expand=True)

        # Find the row control that contains the old plot image
        for control in self.tab2_controls.controls:
            if isinstance(control, ft.Row) and self.plot_image_sp in control.controls:
                row_control = control
                break

        # Find the index of the old plot image in the row control
        plot_image_index = row_control.controls.index(self.plot_image_sp)

        # Replace the old plot image with the new one in the row control
        row_control.controls[plot_image_index] = new_plot_image

        # Update the instance variable to point to the new plot image
        self.plot_image_sp = new_plot_image

        self.page.update()

if __name__ == "__main__":
    ft.app(target=main)


# In[ ]:


ON MY OFFICE MAC , IT IS NOT WORKING
get_ipython().set_next_input('How can I access it to check the issue');get_ipython().run_line_magic('pinfo', 'issue')


# In[ ]:


THINKING

