import random


def monte_carlo_simulation(story_points, iteration_length, team_velocity, resource_utilization, num_simulations):
    results = []

    for _ in range(num_simulations):
        total_story_points = story_points
        days_elapsed = 0


        while total_story_points > 0:
            iteration_story_points = min(total_story_points, team_velocity)
            iteration_days = iteration_length * resource_utilization
            days_elapsed += iteration_days
            total_story_points -= iteration_story_points

        results.append(days_elapsed)

    return results


# Example usage
story_points = [11, 9, 19, 14, 17, 13, 12]
iteration_length = 14
team_velocity = 12
resource_utilization = 1.3
num_simulations = 10000

simulation_results = monte_carlo_simulation(story_points, iteration_length, team_velocity, resource_utilization,
                                            num_simulations)

# Calculate percentiles and date range
confidence_level = 90  # 90% confidence level
lower_percentile = (100 - confidence_level) / 2
upper_percentile = 100 - lower_percentile

sorted_results = sorted(simulation_results)
lower_bound = sorted_results[int(lower_percentile / 100 * num_simulations)]
upper_bound = sorted_results[int(upper_percentile / 100 * num_simulations)]

print(f"{confidence_level}% confidence interval: {lower_bound} - {upper_bound} days")
