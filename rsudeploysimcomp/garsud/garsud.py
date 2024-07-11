import random

import pygad


class GARSUD:
    def __init__(
        self,
        grid_size,
        num_generations=100,
        num_parents_mating=5,
        sol_per_pop=20,
        num_genes=10,
        mutation_percent_genes=10,
    ):
        self.num_generations = num_generations
        self.num_parents_mating = num_parents_mating
        self.sol_per_pop = sol_per_pop
        self.num_genes = num_genes
        self.mutation_percent_genes = mutation_percent_genes
        self.ga_instance = None
        self.initial_population = self._generate_initial_population()
        self.grid_size = grid_size
        self.number_locations = grid_size * grid_size

    def _generate_initial_population(self):
        # Generate random initial population (deployments)
        return [
            [random.randint(1, self.number_locations) for _ in range(self.num_genes)]
            for _ in range(self.sol_per_pop)
        ]

    def fitness_func(self, solution, solution_idx):
        return sum(solution)

    def setup_ga(self):
        # Create an instance of the pygad.GA class with the parameters defined above
        self.ga_instance = pygad.GA(
            num_generations=self.num_generations,
            num_parents_mating=self.num_parents_mating,
            fitness_func=self.fitness_func,
            sol_per_pop=self.sol_per_pop,
            num_genes=self.num_genes,
            initial_population=self.initial_population,
            parent_selection_type="sss",  # Steady State Selection
            keep_parents=2,  # Number of parents to keep in the next population
            crossover_type="single_point",
            mutation_type="random",
            mutation_percent_genes=self.mutation_percent_genes,
        )

    def run(self):
        # Run the genetic algorithm to perform the optimization
        self.ga_instance.run()

    def get_best_solution(self):
        # Get the best solution found and its fitness
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        return solution, solution_fitness

    def print_best_solution(self):
        solution, solution_fitness = self.get_best_solution()
        print(f"Best solution: {solution}")
        print(f"Fitness of the best solution: {solution_fitness}")


# Usage example:
if __name__ == "__main__":
    garsud = GARSUD(
        num_generations=100, num_parents_mating=5, sol_per_pop=20, num_genes=10, mutation_percent_genes=10
    )
    garsud.setup_ga()
    garsud.run()
    garsud.print_best_solution()
