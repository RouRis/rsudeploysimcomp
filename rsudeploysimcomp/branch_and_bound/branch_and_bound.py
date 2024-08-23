import numpy as np

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface, generate_deployment_file
from rsudeploysimcomp.utils.utils import adjust_coordinates_by_offsets, find_closest_junction, load_config


class BranchAndBound:
    def __init__(self, sumoparser):
        self.config = load_config()
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
        self.num_rsus = self.config["general"]["num_rsus"]  # number of RSUs to be deployed
        self.sumoparser = sumoparser
        self.grid_size = sumoparser.grid_size
        self.num_locations = self.grid_size * self.grid_size
        self.optimal_value = -1
        self.optimal_solution = None
        self.picked_junctions = []
        self.rsu_sim_interface = RSU_SIM_Interface()

    # Placeholder for the actual objective function
    def objective_function(self, solution):
        # Example: minimize the negative sum (simulating coverage maximization)
        junctions = self.to_junction_coordinates(solution)
        generate_deployment_file(junctions, self.deployment_csv_path, self.deployment_parquet_path)
        self.rsu_sim_interface.trigger_rsu_simulator()
        coverage, avg_distance = self.rsu_sim_interface.get_metrics_from_simulator()
        return coverage / avg_distance

    # Placeholder for checking if a solution is feasible
    def is_feasible(self, x):
        # Example constraint: no more than 3 RSUs
        return sum(x) <= self.num_rsus

    # Lower bound calculation (a simple heuristic)
    def calculate_lower_bound(self, x):
        return self.objective_function(x)

    def to_junction_coordinates(self, x):
        grid_coords = self.vector_to_grid_coords(x)
        return self.grid_coord_to_junction_coordinates(grid_coords)

    def vector_to_grid_coords(self, vector):
        grid_coords = []
        for index, value in enumerate(vector):
            if value == 1:  # RSU is placed at this grid position
                row = index // self.grid_size
                col = index % self.grid_size
                grid_coords.append((row, col))
        return grid_coords

    def grid_coord_to_junction_coordinates(self, solution):
        junctions = []
        for x, y in solution:
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)
            adjusted_center_x, adjusted_center_y = adjust_coordinates_by_offsets(self.sumoparser, rsu_location)
            junctions.append((adjusted_center_x, adjusted_center_y))
        return junctions

    def run(self):
        # Initial setup
        F = float("inf")  # Initialize to infinity
        best_solution = None

        i = 0
        # Fathomed nodes (start with the root node representing no RSUs)
        fathomed_nodes = [np.zeros(self.num_locations)]  # Example with 5 potential RSU locations
        while fathomed_nodes:
            i += 1
            current_node = fathomed_nodes.pop()
            # Branching (generate new nodes)
            new_nodes = []
            for i in range(len(current_node)):
                if current_node[i] == 0:  # Branch by considering an RSU at position i
                    new_node = current_node.copy()
                    new_node[i] = 1
                    new_nodes.append(new_node)

            # Evaluate the lower bound for each new node
            for node in new_nodes:
                LB = self.calculate_lower_bound(node)

                if self.is_feasible(node) and LB < F:
                    F = LB
                    best_solution = node

                # If node's lower bound indicates a potential improvement, add it to the list
                if LB < F:
                    fathomed_nodes.append(node)

        self.optimal_solution = best_solution
        self.picked_junctions = self.to_junction_coordinates(best_solution)
        self.optimal_value = F
