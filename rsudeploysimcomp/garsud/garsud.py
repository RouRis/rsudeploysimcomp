import random

import pygad

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface, generate_deployment_file, \
    run_pipeline
from rsudeploysimcomp.utils.utils import adjust_coordinates_by_offsets, find_closest_junction, load_config


class GARSUD:
    def __init__(self, sumoparser):
        print("GARSUD Initialization...\n")

        self.name = 'GARSUD'
        self.config = load_config()
        self.ga_instance = None
        self.picked_junctions = []
        self.sumoparser = sumoparser
        self.rsu_sim_interface = RSU_SIM_Interface()
        self.coverage = -1
        self.avg_distance = -1

        self.num_generations = self.config["garsud"]["num_generations"]
        self.num_parents_mating = self.config["garsud"]["num_parents_mating"]
        self.sol_per_pop = self.config["garsud"]["sol_per_pop"]
        self.num_rsus = self.config["general"]["num_rsus"]
        self.grid_size = self.config["general"]["grid_size"]
        self.number_locations = self.grid_size * self.grid_size
        self.mutation_probability = 1.0 / self.num_rsus
        self.keep_parents = int(self.sol_per_pop / 2)

        self.initial_population = self._generate_initial_population()

        self.base_path = self.config["general"]["base_path"]
        self.deployment_csv_path = (
                self.config["general"]["base_path"]
                + self.config["rsu_interface"]["input_path"]
                + self.config["rsu_interface"]["scenario"]
                + self.config["rsu_interface"]["deployment_csv_path"]
        )

        self.deployment_parquet_path = (
                self.config["general"]["base_path"]
                + self.config["rsu_interface"]["input_path"]
                + self.config["rsu_interface"]["scenario"]
                + self.config["rsu_interface"]["deployment_parquet_path"]
        )

    def _generate_initial_population(self):
        # Generate random initial population (deployments)
        return [
            [random.randint(1, self.number_locations) for _ in range(self.num_rsus)]
            for _ in range(self.sol_per_pop)
        ]

    def fitness_func(self, ga_instance, solution, solution_idx):
        coverage, avg_distance = self.solution_to_metrics(solution)
        return coverage, -avg_distance

    def setup_ga(self):
        # Define the callback function to provide feedback after each generation
        def on_generation(ga_instance):
            solution, solution_fitness, _ = ga_instance.best_solution()
            print(f"Generation {ga_instance.generations_completed}:")
            print(f"    Best solution so far: {solution}")
            print(f"    Fitness of the best solution so far: {solution_fitness}")
            self.picked_junctions = self.grid_index_to_junction_coordinates(solution)
            # self.plotter.plot_deployment(self.picked_junctions, "Garsud: Generation "
            #                              + str(ga_instance.generations_completed))

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
        # Run the genetic algorithm to perform the optimization
        self.ga_instance.run()
        # Convert Genotype (Indices of grids) to Phenotype (x,y of actual junctions)
        solution, _, _ = self.ga_instance.best_solution()
        self.picked_junctions = self.grid_index_to_junction_coordinates(solution)
        self.coverage, self.avg_distance = self.solution_to_metrics(solution)

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
        coverage, avg_distance = run_pipeline(algorithm_name=self.name,
                                              picked_junctions=junctions,
                                              deployment_csv_path=self.deployment_csv_path,
                                              deployment_parquet_path=self.deployment_parquet_path,
                                              rsu_sim_interface=self.rsu_sim_interface)
        return coverage, avg_distance
