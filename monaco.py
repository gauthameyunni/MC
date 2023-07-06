import monaco
import numpy as np

# Define the variables and their distributions
cycle_time_mean = 5  # Mean cycle time in days
cycle_time_std = 1  # Standard deviation of cycle time in days

throughput_mean = 4  # Mean throughput in work items per day
throughput_std = 1  # Standard deviation of throughput in work items per day

work_item_size_mean = 2  # Mean work item size in days
work_item_size_std = 0.5  # Standard deviation of work item size in days

num_simulations = 5000  # Number of simulation iterations

# Generate random samples for the variables
cycle_time_samples = np.random.normal(cycle_time_mean, cycle_time_std, num_simulations)
throughput_samples = np.random.normal(throughput_mean, throughput_std, num_simulations)
work_item_size_samples = np.random.normal(work_item_size_mean, work_item_size_std, num_simulations)

# Perform the Monte Carlo simulation
results = []
for i in range(num_simulations):
    # Calculate cycle time based on random samples
    cycle_time = cycle_time_samples[i]

    # Calculate throughput based on random samples
    throughput = throughput_samples[i]

    # Calculate work item size based on random samples
    work_item_size = work_item_size_samples[i]

    # Calculate lead time based on cycle time and work item size
    lead_time = cycle_time + work_item_size

    # Calculate the number of work items completed based on throughput
    num_completed_items = throughput * cycle_time

    # Append the results to the list
    results.append({
        'Cycle Time': cycle_time,
        'Throughput': throughput,
        'Lead Time': lead_time,
        'Work Item Size': work_item_size,
        'Completed Items': num_completed_items
    })

# Analyze the results
cycle_time_mean = np.mean([result['Cycle Time'] for result in results])
throughput_mean = np.mean([result['Throughput'] for result in results])
lead_time_mean = np.mean([result['Lead Time'] for result in results])
work_item_size_mean = np.mean([result['Work Item Size'] for result in results])
completed_items_mean = np.mean([result['Completed Items'] for result in results])

# Print the mean values of the metrics
print("Mean Cycle Time:", cycle_time_mean)
print("Mean Throughput:", throughput_mean)
print("Mean Lead Time:", lead_time_mean)
print("Mean Work Item Size:", work_item_size_mean)
print("Mean Completed Items:", completed_items_mean)
