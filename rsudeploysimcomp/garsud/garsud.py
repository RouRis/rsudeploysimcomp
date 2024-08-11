import random
import os
import pygad

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface
from rsudeploysimcomp.utils.utils import adjust_coordinates_with_offsets, find_closest_junction, load_config


class GARSUD:
    def __init__(self, sumoparser, num_generations=100, num_parents_mating=10, sol_per_pop=20, num_rsus=10):
        self.num_generations = num_generations
        self.num_parents_mating = num_parents_mating
        self.sol_per_pop = sol_per_pop
        self.num_rsus = num_rsus
        self.ga_instance = None
        self.grid_size = sumoparser.grid_size
        self.number_locations = self.grid_size * self.grid_size
        self.mutation_probability = 1.0 / num_rsus
        self.keep_parents = int(sol_per_pop / 2)
        self.initial_population = self._generate_initial_population()
        self.sumoparser = sumoparser
        self.picked_junctions = []
        self.rsu_sim_interface = RSU_SIM_Interface()
        self.config = load_config()
        self.deployment_csv_name = self.config["garsud"]["deployment_csv"]
        self.deployment_parquet_name = self.config["garsud"]["deployment_parquet"]

    def _generate_initial_population(self):
        # Generate random initial population (deployments)
        return [
            [random.randint(1, self.number_locations) for _ in range(self.num_rsus)]
            for _ in range(self.sol_per_pop)
        ]

    def fitness_func(self, ga_instance, solution, solution_idx):
        # generate junctions out of current solution
        junctions = self.grid_index_to_junction_coordinates(solution)
        # generate Deployment Input Files
        self.rsu_sim_interface.generate_deployment_file(junctions, self.deployment_csv_name,
                                                        self.deployment_parquet_name)
        self.rsu_sim_interface.trigger_rsu_simulotor()
        coverage, avg_distance = self.rsu_sim_interface.get_metrics_from_simulator()
        return coverage, -avg_distance

    def setup_ga(self):
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
        )

    def run(self):
        # Run the genetic algorithm to perform the optimization
        self.ga_instance.run()
        # Convert Genotype (Indices of grids) to Phenotype (x,y of actual junctions)
        solution, _, _ = self.ga_instance.best_solution()
        self.picked_junctions = self.grid_index_to_junction_coordinates(solution)

    def grid_index_to_junction_coordinates(self, solution):
        junctions = []
        for index in solution:
            x = int(index % self.grid_size)
            y = int(index // self.grid_size)
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)
            adjusted_center_x, adjusted_center_y = adjust_coordinates_with_offsets(self.sumoparser, rsu_location)
            junctions.append((adjusted_center_x, adjusted_center_y))
        return junctions

    def get_best_solution(self):
        # Get the best solution found and its fitness
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        return solution, solution_fitness

    def print_best_solution(self):
        solution, solution_fitness = self.get_best_solution()
        print(f"Best solution: {solution}")
        print(f"Fitness of the best solution: {solution_fitness}")
