import tkinter as tk
from tkinter import messagebox

from MC4 import monte_carlo_simulation


def run_simulation():
    # Retrieve input values from the GUI
    try:
        story_points = float(story_points_entry.get())
        iteration_length = float(iteration_length_entry.get())
        team_velocity = float(team_velocity_entry.get())
        resource_utilization = float(resource_utilization_entry.get())
        num_simulations = int(num_simulations_entry.get())

        # Perform Monte Carlo simulation
        simulation_results = monte_carlo_simulation(story_points, iteration_length, team_velocity, resource_utilization, num_simulations)

        # Calculate percentiles and date range
        confidence_level = 90  # 9 0% confidence level
        lower_percentile = (100 - confidence_level) / 2
        upper_percentile = 100 - lower_percentile

        sorted_results = sorted(simulation_results)
        lower_bound = sorted_results[int(lower_percentile / 100 * num_simulations)]
        upper_bound = sorted_results[int(upper_percentile / 100 * num_simulations)]

        # Display results in a message box
        message = f"{confidence_level}% confidence interval: {lower_bound} - {upper_bound} days"
        messagebox.showinfo("Simulation Results", message)

    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter numeric values.")

# Create the main window
window = tk.Tk()
window.title("Monte Carlo Simulation")

# Create input labels and entry fields
story_points_label = tk.Label(window, text="Story Points:")
story_points_label.grid(row=0, column=0, padx=10, pady=10)
story_points_entry = tk.Entry(window)
story_points_entry.grid(row=0, column=1, padx=10, pady=10)

iteration_length_label = tk.Label(window, text="Iteration Length (days):")
iteration_length_label.grid(row=1, column=0, padx=10, pady=10)
iteration_length_entry = tk.Entry(window)
iteration_length_entry.grid(row=1, column=1, padx=10, pady=10)

team_velocity_label = tk.Label(window, text="Team Velocity (story points per iteration):")
team_velocity_label.grid(row=2, column=0, padx=10, pady=10)
team_velocity_entry = tk.Entry(window)
team_velocity_entry.grid(row=2, column=1, padx=10, pady=10)

resource_utilization_label = tk.Label(window, text="Resource Utilization (0-1):")
resource_utilization_label.grid(row=3, column=0, padx=10, pady=10)
resource_utilization_entry = tk.Entry(window)
resource_utilization_entry.grid(row=3, column=1, padx=10, pady=10)

num_simulations_label = tk.Label(window, text="Number of Simulations:")
num_simulations_label.grid(row=4, column=0, padx=10, pady=10)
num_simulations_entry = tk.Entry(window)
num_simulations_entry.grid(row=4, column=1, padx=10, pady=10)

run_simulation_button = tk.Button(window, text="Run Simulation", command=run_simulation)
run_simulation_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI event loop
window.mainloop()
