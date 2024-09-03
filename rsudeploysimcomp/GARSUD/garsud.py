import random
import time
from collections import OrderedDict

import pygad

from rsudeploysimcomp.Utils.utils import (
    adjust_coordinates_by_offsets,
    find_closest_junction,
    load_config,
    track_algorith_exec_time,
)
from rsudeploysimcomp.VanetSimulatorInterface.vanet_sim_interface import VanetSimulatorInterface, run_pipeline


class GARSUD:
    def __init__(self, sumoparser):
        print("GARSUD Initialization...\n")
        self.config = load_config()

        self.name = "GARSUD"
        self.ga_instance = None
        self.picked_junctions = []
        self.sumoparser = sumoparser
        self.vanet_simulator_interface = VanetSimulatorInterface()
        self.coverage = -1
        self.avg_distance = -1
        self.best_solution = None
        self.cache_use_counter = 0
        self.fitness_cache = OrderedDict()

        self.num_rsus = self.config["General"]["num_rsus"]
        self.grid_size = self.config["General"]["grid_size"]
        self.rsu_radius = self.config["General"]["rsu_radius"]
        self.optimize_coverage = self.config["Algorithms"]["GARSUD"]["optimization_param"]["coverage"]
        self.optimize_avg_distance = self.config["Algorithms"]["GARSUD"]["optimization_param"]["avg_distance"]
        self.track_exec_time = bool(self.config["Algorithms"]["GARSUD"]["track_exec_time"])
        self.num_generations = self.config["Algorithms"]["GARSUD"]["num_generations"]
        self.num_parents_mating = self.config["Algorithms"]["GARSUD"]["num_parents_mating"]
        self.sol_per_pop = self.config["Algorithms"]["GARSUD"]["sol_per_pop"]
        self.number_locations = self.grid_size * self.grid_size
        self.mutation_probability = 1.0 / self.num_rsus
        self.keep_parents = self.config["Algorithms"]["GARSUD"]["keep_parents"]
        self.base_path = self.config["General"]["base_path"]
        self.deployment_csv_path = (
            self.config["General"]["base_path"]
            + self.config["VanetInterface"]["input_path"]
            + self.config["VanetInterface"]["scenario"]
            + self.config["VanetInterface"]["deployment_csv_path"]
        )
        self.deployment_parquet_path = (
            self.config["General"]["base_path"]
            + self.config["VanetInterface"]["input_path"]
            + self.config["VanetInterface"]["scenario"]
            + self.config["VanetInterface"]["deployment_parquet_path"]
        )
        self.initial_population = self._generate_initial_population()

    def _generate_initial_population(self):
        # Generate random initial population (deployments)
        return [
            [random.randint(1, self.number_locations) for _ in range(self.num_rsus)]
            for _ in range(self.sol_per_pop)
        ]

    def fitness_func(self, ga_instance, solution, solution_idx):
        solution_tuple = tuple(solution)  # Convert solution to a tuple to make it hashable for the cache
        # Check if the fitness of the solution is in the cache
        if solution_tuple in self.fitness_cache:
            self.cache_use_counter += 1
            print(f"Fitness cache hit - #{self.cache_use_counter}")
            coverage, avg_distance = self.fitness_cache[solution_tuple]
        else:
            # Calculate the fitness if not in cache
            coverage, avg_distance = self.solution_to_metrics(solution)
        self.fitness_cache[solution_tuple] = (coverage, avg_distance)
        if self.optimize_coverage and self.optimize_avg_distance:
            return coverage, -avg_distance
        elif self.optimize_coverage:
            return coverage
        else:
            return -avg_distance

    def setup_ga(self):
        # Define the callback function to provide feedback after each generation
        def on_generation(ga_instance):
            solution, solution_fitness, _ = ga_instance.best_solution()
            self.best_solution = ga_instance.best_solution()
            print(f"Generation {ga_instance.generations_completed}:")
            print(f"    Fitness of the best solution so far: {solution_fitness}")
            self.picked_junctions = self.grid_index_to_junction_coordinates(solution)

        # Create an instance of the pygad.GA class with the parameters defined above
        self.ga_instance = pygad.GA(
            num_generations=self.num_generations,
            num_parents_mating=self.num_parents_mating,
            fitness_func=self.fitness_func,
            sol_per_pop=self.sol_per_pop,
            num_genes=self.num_rsus,
            initial_population=self.initial_population,
            parent_selection_type="tournament",  # Steady State Selection
            keep_parents=self.keep_parents,  # Number of parents to keep in the next population
            crossover_type="single_point",
            mutation_type="random",
            mutation_probability=self.mutation_probability,
            gene_space=range(0, self.number_locations),
            on_generation=on_generation,
        )

    def run(self):
        start_segment_time = -1
        if self.track_exec_time:
            start_segment_time = time.perf_counter()

        # Run the genetic algorithm to perform the optimization
        self.ga_instance.run()
        # Convert Genotype (Indices of grids) to Phenotype (x,y of actual junctions)
        solution, solution_fitness, _ = self.ga_instance.best_solution()
        sol2, sol2_fitness, _ = self.best_solution
        self.picked_junctions = self.grid_index_to_junction_coordinates(solution)
        if self.optimize_coverage and self.optimize_avg_distance:
            self.coverage = solution_fitness[0]
            self.avg_distance = solution_fitness[1]
        elif self.optimize_coverage:
            if solution_fitness < sol2_fitness:
                self.coverage = sol2_fitness
            else:
                self.coverage = solution_fitness
        else:
            self.avg_distance = solution_fitness

        if self.track_exec_time:
            track_algorith_exec_time(start_segment_time, self)

    def grid_index_to_junction_coordinates(self, solution):
        junctions = []
        for index in solution:
            x = int(index % self.grid_size)
            y = int(index // self.grid_size)
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)
            adjusted_center_x, adjusted_center_y = adjust_coordinates_by_offsets(self.sumoparser, rsu_location)
            junctions.append((adjusted_center_x, adjusted_center_y))
        return junctions

    def solution_to_metrics(self, solution):
        junctions = self.grid_index_to_junction_coordinates(solution)
        # generate Deployment Input Files
        coverage, avg_distance = run_pipeline(
            picked_junctions=junctions,
            deployment_csv_path=self.deployment_csv_path,
            deployment_parquet_path=self.deployment_parquet_path,
            rsu_sim_interface=self.vanet_simulator_interface,
        )
        return coverage, avg_distance
