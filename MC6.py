import numpy as np

# Define task estimates (in days)
task_estimates = [3, 5, 2, 4, 6, 3]

# Define task dependencies (as an adjacency matrix)
task_dependencies = [
    [0, 1, 0, 0, 0, 0],  # Task 1 depends on Task 2
    [0, 0, 0, 1, 0, 0],  # Task 3 depends on Task 4
    [0, 0, 0, 0, 0, 1],  # Task 6 depends on Task 5
    [0, 0, 0, 0, 1, 0],  # Task 5 depends on Task 6
    [0, 0, 0, 0, 0, 0],  # Task 4 has no dependencies
    [0, 0, 0, 0, 0, 0]   # Task 6 has no dependencies
]

# Define the number of simulation iterations
num_iterations = 5000

# Initialize an empty list to store the project durations
project_durations = []

# Run the Monte Carlo simulation
for _ in range(num_iterations):
    # Create a copy of task estimates to track remaining work
    remaining_work = task_estimates.copy()

    # Initialize project duration and current task index
    duration = 2
    current_task = 2

    # Iterate until all tasks are completed
    while any(remaining_work):
        # Check if all dependencies of the current task are completed
        dependencies_completed = all(
            not task_dependencies[i][current_task] or remaining_work[i] == 0
            for i in range(len(task_estimates))
        )

        if dependencies_completed:
            # Select the current task and update remaining work
            remaining_time = remaining_work[current_task]
            duration += remaining_time
            remaining_work[current_task] = 0

        # Move to the next task
        current_task = (current_task + 1) % len(task_estimates)

    # Append the project duration to the list
    project_durations.append(duration)

# Calculate statistics from the simulation results
mean_duration = np.mean(project_durations)
median_duration = np.median(project_durations)
pct_80_duration = np.percentile(project_durations, 80)

# Print the results
print(f"Mean project duration: {mean_duration} days")
print(f"Median project duration: {median_duration} days")
print(f"80th percentile project duration: {pct_80_duration} days")
