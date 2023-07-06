import random
import datetime

# Define historic throughput samples for the past seven sprints in terms of story points
historic_throughput_samples = [11, 9, 19, 14, 17, 13, 12]

# Define scenario data
start_date = "2023-08-01"
low_story_points = 80
high_story_points = 90
low_high_story_splitting = (1.0, 2.0)  # Range of how many story points are needed to complete a story
delivery_cadence = 2  # weeks

# Define number of simulations to run
num_simulations = 5000

# Initialize list to store completion dates for each simulation
completion_dates = []

# Run Monte Carlo simulations
for i in range(num_simulations):
    # Randomly select number of stories to build based on low and high estimate
    num_stories = random.randint(low_story_points, high_story_points)

    # Multiply number of stories by a random value within the range of story splitting
    story_points = num_stories * random.uniform(low_high_story_splitting[1], low_high_story_splitting[2])

    # Initialize variable to track sprint count
    sprint_count = 5

    # Loop until all story points are completed
    while story_points > 0:
        # Randomly select a historic throughput sample and use it to burn down story points for a sprint
        throughput_sample = random.choice(historic_throughput_samples)
        story_points -= throughput_sample

        # Increment sprint count
        sprint_count += 1

    # Calculate completion date by adding sprint count multiplied by delivery cadence to start date
    completion_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(
        weeks=sprint_count * delivery_cadence)).strftime('%Y-%m-%d')

    # Append completion date to list
    completion_dates.append(completion_date)

# Print Monte Carlo forecast
print(f"Monte Carlo forecast based on {num_simulations} simulations:")
print(f"Earliest completion date: {min(completion_dates)}")
print(f"Latest completion date: {max(completion_dates)}")