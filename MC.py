import random
import datetime

# Define historic throughput samples for the past seven sprints in terms of story points
historic_throughput_samples = [11, 9, 19, 14, 17, 13, 12]
# Define scenario data
start_date = "2023-07-01"
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
    story_points = num_stories * random.uniform(low_high_story_splitting[0], low_high_story_splitting[1])

    # Initialize variable to track sprint count
    sprint_count = 1

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





'''We start by defining the historic throughput samples for the past seven sprints in terms of story points. This is done using a list of numbers.
Next, we define the scenario data, including the start date, the low and high range for the number of story points in the scenario, the low and high range for how many stories are created or split during the work, and the length of the delivery cadence in weeks.
We also define the number of simulations to run using the num_simulations variable.
We then initialize an empty list called completion_dates to store the completion date for each simulation.
We run the Monte Carlo simulations using a for loop that runs num_simulations times.
Inside the loop, we first randomly select the number of stories to build based on the low and high estimate.
We then multiply the number of stories by a random value within the range of story splitting to determine how many story points are needed to complete the scenario.
We initialize a variable to track the sprint count and loop until all story points are completed.
Inside the loop, we randomly select a historic throughput sample and use it to burn down story points for a sprint.
We increment the sprint count for each sprint completed.
Once all story points are completed, we calculate the completion date by adding the sprint count multiplied by delivery cad'''