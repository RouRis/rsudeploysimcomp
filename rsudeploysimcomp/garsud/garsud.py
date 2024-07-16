import random

import pygad

from rsudeploysimcomp.utils.utils import find_closest_junction


class GARSUD:
    def __init__(
        self, sumoparser, grid_size=9, num_generations=100, num_parents_mating=10, sol_per_pop=20, num_rsus=10
    ):
        self.num_generations = num_generations
        self.num_parents_mating = num_parents_mating
        self.sol_per_pop = sol_per_pop
        self.num_rsus = num_rsus
        self.ga_instance = None
        self.grid_size = grid_size
        self.number_locations = grid_size * grid_size
        self.mutation_probability = 1.0 / num_rsus
        self.keep_parents = int(sol_per_pop / 2)
        self.initial_population = self._generate_initial_population()
        self.sumoparser = sumoparser
        self.picked_junctions = []

    def _generate_initial_population(self):
        # Generate random initial population (deployments)
        return [
            [random.randint(1, self.number_locations) for _ in range(self.num_rsus)]
            for _ in range(self.sol_per_pop)
        ]

    def fitness_func(self, ga_instance, solution, solution_idx):
        return sum(solution)

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
            gene_space=range(1, self.number_locations + 1),
        )

    def run(self):
        # Run the genetic algorithm to perform the optimization
        self.ga_instance.run()
        # Convert Genotype (Indices of grids) to Phenotype (x,y of actual junctions)
        solution, _, _ = self.ga_instance.best_solution()
        self.grid_index_to_junction_coordinates(solution)

    def grid_index_to_junction_coordinates(self, solution):
        junctions = []
        for index in solution:
            x = int(index % self.grid_size)
            y = int(index // self.grid_size)
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            closest_junction = find_closest_junction(self.sumoparser, center_x, center_y)
            junctions.append(closest_junction)
        self.picked_junctions = junctions

    def get_best_solution(self):
        # Get the best solution found and its fitness
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        return solution, solution_fitness

    def print_best_solution(self):
        solution, solution_fitness = self.get_best_solution()
        print(f"Best solution: {solution}")
        print(f"Fitness of the best solution: {solution_fitness}")
