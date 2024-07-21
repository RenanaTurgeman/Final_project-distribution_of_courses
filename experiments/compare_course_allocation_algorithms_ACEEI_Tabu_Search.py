"""
Compare the performance of algorithms for fair course allocation.

Programmer: Erel Segal-Halevi
Since: 2023-07
"""


######### COMMON VARIABLES AND ROUTINES ##########

from fairpyx import divide, AgentBundleValueMatrix, Instance
import fairpyx.algorithms as crs
from typing import *
import numpy as np

max_value = 1000
normalized_sum_of_values = 1000
TIME_LIMIT = 100

from fairpyx.algorithms.ACEEI_algorithms.ACEEI import ACEEI_without_EFTB, ACEEI_with_EFTB, ACEEI_with_contested_EFTB
from fairpyx.algorithms.ACEEI_algorithms.tabu_search import run_tabu_search

algorithms_to_check = [
    ACEEI_without_EFTB,
    ACEEI_with_EFTB,
    ACEEI_with_contested_EFTB,
    run_tabu_search,
    crs.iterated_maximum_matching_adjusted,
    crs.bidirectional_round_robin,
]

def evaluate_algorithm_on_instance(algorithm, instance):
    allocation = divide(algorithm, instance)
    matrix = AgentBundleValueMatrix(instance, allocation)
    matrix.use_normalized_values()
    return {
        "utilitarian_value": matrix.utilitarian_value(),
        "egalitarian_value": matrix.egalitarian_value(),
        "max_envy": matrix.max_envy(),
        "mean_envy": matrix.mean_envy(),
        "max_deficit": matrix.max_deficit(),
        "mean_deficit": matrix.mean_deficit(),
        "num_with_top_1": matrix.count_agents_with_top_rank(1),
        "num_with_top_2": matrix.count_agents_with_top_rank(2),
        "num_with_top_3": matrix.count_agents_with_top_rank(3),
    }



######### EXPERIMENT WITH UNIFORMLY-RANDOM DATA ##########

def course_allocation_with_random_instance_uniform(
    num_of_agents:int, num_of_items:int, 
    value_noise_ratio:float,
    algorithm:Callable,
    random_seed: int,):
    agent_capacity_bounds =  [6,6]
    item_capacity_bounds = [40,40]    
    np.random.seed(random_seed)
    instance = Instance.random_uniform(
        num_of_agents=num_of_agents, num_of_items=num_of_items, 
        normalized_sum_of_values=normalized_sum_of_values,
        agent_capacity_bounds=agent_capacity_bounds, 
        item_capacity_bounds=item_capacity_bounds, 
        item_base_value_bounds=[1,max_value],
        item_subjective_ratio_bounds=[1-value_noise_ratio, 1+value_noise_ratio]
        )
    return evaluate_algorithm_on_instance(algorithm, instance)

def run_uniform_experiment():
    # Run on uniformly-random data:
    experiment = experiments_csv.Experiment("results/", "course_allocation_uniform.csv", backup_folder="results/backup/")
    input_ranges = {
        "num_of_agents": [5, 8, 10],
        "num_of_items":  [4, 6],
        "value_noise_ratio": [0.2],
        "algorithm": algorithms_to_check,
        "random_seed": range(5),
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges, time_limit=TIME_LIMIT)



######### EXPERIMENT WITH DATA GENERATED ACCORDING TO THE SZWS MODEL ##########

def course_allocation_with_random_instance_szws(
    num_of_agents:int, num_of_items:int, 
    agent_capacity:int,
    supply_ratio:float,
    num_of_popular_items:int,
    mean_num_of_favorite_items:float,
    favorite_item_value_bounds:tuple[int,int],
    nonfavorite_item_value_bounds:tuple[int,int],
    algorithm:Callable,
    random_seed: int,):
    np.random.seed(random_seed)
    instance = Instance.random_szws(
        num_of_agents=num_of_agents, num_of_items=num_of_items, normalized_sum_of_values=normalized_sum_of_values,
        agent_capacity=agent_capacity, 
        supply_ratio=supply_ratio, 
        num_of_popular_items=num_of_popular_items,
        mean_num_of_favorite_items=mean_num_of_favorite_items,
        favorite_item_value_bounds=favorite_item_value_bounds,
        nonfavorite_item_value_bounds=nonfavorite_item_value_bounds,
        )
    return evaluate_algorithm_on_instance(algorithm, instance)

def run_szws_experiment():
    # Run on SZWS simulated data:
    experiment = experiments_csv.Experiment("results/", "course_allocation_szws_ACEEI.csv", backup_folder="results/backup/")
    input_ranges = {
        "num_of_agents": [10, 20, 30, 40],
        "num_of_items":  [5, 10, 14],                            # in SZWS: 25
        "agent_capacity": [5, 7, 9],                            # as in SZWS
        "supply_ratio": [1.1, 1.25, 1.5],                    # as in SZWS
        "num_of_popular_items": [6, 9],                   # as in SZWS
        "mean_num_of_favorite_items": [2.6, 3.85],        # as in SZWS code https://github.com/marketdesignresearch/Course-Match-Preference-Simulator/blob/main/preference_generator_demo.ipynb
        "favorite_item_value_bounds": [(50,100)],         # as in SZWS code https://github.com/marketdesignresearch/Course-Match-Preference-Simulator/blob/main/preference_generator.py
        "nonfavorite_item_value_bounds": [(0,50)],        # as in SZWS code https://github.com/marketdesignresearch/Course-Match-Preference-Simulator/blob/main/preference_generator.py
        "algorithm": algorithms_to_check,
        "random_seed": range(5),
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_szws, input_ranges, time_limit=TIME_LIMIT)



######### EXPERIMENT WITH DATA SAMPLED FROM ARIEL 5783 DATA ##########

import json
filename = "data/ariel_5783_input.json"
with open(filename, "r", encoding="utf-8") as file:
    ariel_5783_input = json.load(file)

def course_allocation_with_random_instance_sample(
    max_total_agent_capacity:int, 
    algorithm:Callable,
    random_seed: int,):
    np.random.seed(random_seed)

    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts) = \
        (ariel_5783_input["valuations"], ariel_5783_input["agent_capacities"], ariel_5783_input["item_capacities"], ariel_5783_input["agent_conflicts"], ariel_5783_input["item_conflicts"])
    instance = Instance.random_sample(
        max_num_of_agents = max_total_agent_capacity, 
        max_total_agent_capacity = max_total_agent_capacity,
        prototype_agent_conflicts=agent_conflicts,
        prototype_agent_capacities=agent_capacities, 
        prototype_valuations=valuations,
        item_capacities=item_capacities,
        item_conflicts=item_conflicts)
    return evaluate_algorithm_on_instance(algorithm, instance)

def run_ariel_experiment():
    # Run on Ariel sample data:
    experiment = experiments_csv.Experiment("results/", "course_allocation_ariel.csv", backup_folder="results/backup/")
    input_ranges = {
        "max_total_agent_capacity": [1000, 1115, 1500, 2000], # in reality: 1115
        "algorithm": algorithms_to_check,
        "random_seed": range(10),
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_sample, input_ranges, time_limit=TIME_LIMIT)

import pandas as pd
import matplotlib.pyplot as plt

# Function to load experiment results from CSV
def load_experiment_results(filename):
    df = pd.read_csv(filename)
    return df

# Function to plot average runtime vs. number of students
def plot_average_runtime_vs_students(df, algorithm_name):
    average_runtime = df.groupby('num_of_agents')['runtime'].mean()
    num_of_agents = average_runtime.index
    runtime = average_runtime.values

    plt.plot(num_of_agents, runtime, marker='o', label=algorithm_name)
    plt.xlabel('Number of Students')
    plt.ylabel('Average Runtime (seconds)')
    plt.title(f'Average Runtime vs. Number of Students')
    plt.legend()
    plt.grid(True)

######### MAIN PROGRAM ##########

if __name__ == "__main__":
    import logging, experiments_csv
    experiments_csv.logger.setLevel(logging.INFO)
    # run_uniform_experiment()
    run_szws_experiment()
    # run_ariel_experiment()

    # Load and plot data for run_uniform_experiment()
    # uniform_results = load_experiment_results('results/course_allocation_uniform.csv')
    # plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    #
    # for algorithm in algorithms_to_check:
    #     algorithm_name = algorithm.__name__
    #     algorithm_data = uniform_results[uniform_results['algorithm'] == algorithm_name]
    #     plot_average_runtime_vs_students(algorithm_data, algorithm_name)
    #
    # plt.tight_layout()
    # plt.show()

    # Load and plot data for run_szws_experiment()
    szws_results = load_experiment_results('results/course_allocation_szws_ACEEI.csv')
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed

    for algorithm in algorithms_to_check:
        algorithm_name = algorithm.__name__
        algorithm_data = szws_results[szws_results['algorithm'] == algorithm_name]
        plot_average_runtime_vs_students(algorithm_data, algorithm_name)

    plt.tight_layout()
    plt.show()

