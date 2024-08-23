import numpy as np

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface, generate_deployment_file
from rsudeploysimcomp.utils.utils import adjust_coordinates_by_offsets, find_closest_junction, load_config


class PMCB_P:
    def __init__(self, sumoparser):
        self.config = load_config()
        self.rsu_sim_interface = RSU_SIM_Interface()
        self.coverage = -1
        self.avg_distance = -1
        self.sumoparser = sumoparser
        self.grid_size = sumoparser.grid_size  # Number of cells per dimension
        self.M = sumoparser.M  # 2D array with vehicle counts
        self.P = sumoparser.P  # 2D array (sparsed) with migration ratios between locations
        self.num_rsus = self.config["general"]["num_rsus"]  # Maximum number of RSUs to be deployed
        self.location_flows = np.zeros((self.grid_size, self.grid_size))
        self.remaining_locations = set((x, y) for x in range(self.grid_size) for y in range(self.grid_size))
        self.picked_locations = set()
        self.picked_junctions = set()
        self.rsu_counter = 0
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

    def run(self):
        while self.rsu_counter < self.num_rsus and len(self.remaining_locations) > 0:
            self.update_projected_flows()
            self.pick_next_location()
            self.rsu_counter += 1
        generate_deployment_file(self.picked_junctions, self.deployment_csv_path, self.deployment_parquet_path)
        self.rsu_sim_interface.trigger_rsu_simulator()
        self.coverage, self.avg_distance = self.rsu_sim_interface.get_metrics_from_simulator()

    def update_projected_flows(self):
        # First iteration: Pick the location with the highest vehicle number
        if not self.picked_locations:
            self.location_flows = np.copy(self.M)
        else:
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if (row, col) not in self.picked_locations:
                        projected_flow = self.calculate_projection((row, col))
                        self.location_flows[row, col] = projected_flow
                    else:
                        self.location_flows[row, col] = -1

    def calculate_projection(self, location):
        row, col = location
        total_flow = self.M[row, col]  # Start with the current vehicle count at the location

        # Directions: left-right, right-left, bottom-up, top-down
        # No diagonal: because of very small migration events
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            total_flow += self.propagate_flow(location, direction)

        return total_flow

    def propagate_flow(self, start_location, direction):
        row, col = start_location
        d_row, d_col = direction
        total_flow = 0
        compound_prob = 1

        while 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if (row, col) != start_location:  # Skip the initial location
                total_flow += self.M[row, col] * compound_prob
            row += d_row
            col += d_col
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                compound_prob *= self.P[row, col]  # Update the compounded probability

        return total_flow

    def pick_next_location(self):
        # Find the location with the highest projected flow
        next_location = np.unravel_index(np.argmax(self.location_flows, axis=None), self.location_flows.shape)

        # Get the junction closest to the center of the grid cell
        center_x = (next_location[0] + 0.5) * (self.sumoparser.x_max / self.grid_size)
        center_y = (next_location[1] + 0.5) * (self.sumoparser.y_max / self.grid_size)
        rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)

        adjusted_center_x, adjusted_center_y = adjust_coordinates_by_offsets(self.sumoparser, rsu_location)

        # Add the best location to picked_locations and remove from all_locations
        self.picked_junctions.add((adjusted_center_x, adjusted_center_y))
        self.picked_locations.add(next_location)
        self.remaining_locations.remove(next_location)
        # generate new M-Matrix with removed handled vehicles
        self.update_M(next_location)
        # print(f"Picked location {next_location} with projected flow {self.location_flows[next_location]}")

    def update_M(self, picked_location):
        location_vehicle = self.sumoparser.location_vehicles[picked_location]
        for vehicle in location_vehicle:
            if vehicle in self.sumoparser.vehicle_paths:
                self.sumoparser.vehicle_paths.pop(vehicle)
        self.M = self.generate_M(self.sumoparser.vehicle_paths)

    def generate_M(self, vehicle_paths):
        new_M = np.zeros((self.grid_size, self.grid_size), dtype=int)  # Reset the matrix
        for vehicle_id, path in vehicle_paths.items():
            for cell in path:
                new_M[cell[0], cell[1]] += 1
        return new_M
