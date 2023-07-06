import random
from datetime import datetime, timedelta

def monte_carlo_forecast(story_points, num_simulations):
    # Set the estimated completion time per story point
    completion_time = timedelta(days=2)  # Modify as needed

    # Perform Monte Carlo simulations
    completion_dates = []
    for _ in range(num_simulations):
        total_time = timedelta()
        for points in story_points:
            time = completion_time * points
            total_time += time
        completion_dates.append(datetime.now() + total_time)

    # Sort completion dates
    completion_dates.sort()

    # Calculate percentiles
    percentiles = [50, 75, 90, 95, 99]
    percentile_dates = []
    for percentile in percentiles:
        index = int((percentile / 100) * num_simulations) - 1
        percentile_dates.append(completion_dates[index])
        

    return percentile_dates

# Example usage
story_points = [3,5,2,4,7,9,13,7,9,3,5, 2, 4,7,9,13,7,9,3,5,2,4,7,9,13,7,9,3,5, 2, 4,7,9,13,7,9,3,5,2,4,7,9,13,7,9,3,5, 2, 4,7,9,13,7,9]  # Modify with your story points
num_simulations = 5000  # Adjust as needed

forecast_dates = monte_carlo_forecast(story_points, num_simulations)

print("Monte Carlo Forecast Dates:")
print(f"50th percentile: {forecast_dates[0]}")
print(f"75th percentile: {forecast_dates[1]}")
print(f"90th percentile: {forecast_dates[2]}")
print(f"95th percentile: {forecast_dates[3]}")
print(f"99th percentile: {forecast_dates[4]}")
