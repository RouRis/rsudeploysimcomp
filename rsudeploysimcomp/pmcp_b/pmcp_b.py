import numpy as np


class PMCB_P:
    def __init__(self, sumoparser, max_rsus):
        self.pmcpBParser = sumoparser
        self.grid_size = sumoparser.grid_size  # Number of cells per dimension
        self.M = sumoparser.M  # 2D array with vehicle counts
        self.P = sumoparser.P  # 2D array (sparsed) with migration ratios between locations
        self.max_rsus = max_rsus  # Maximum number of RSUs to be deployed
        self.location_flows = np.zeros((self.grid_size, self.grid_size))
        self.remaining_locations = set((x, y) for x in range(self.grid_size) for y in range(self.grid_size))
        self.picked_locations = set()
        self.rsu_counter = 0
        self.run()

    def run(self):
        while self.rsu_counter < self.max_rsus and len(self.remaining_locations) > 0:
            self.update_projected_flows()
            self.pick_next_location()
            self.rsu_counter += 1

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

        # Add the best location to picked_locations and remove from all_locations
        self.picked_locations.add(next_location)
        self.remaining_locations.remove(next_location)
        # generate new M-Matrix with removed handled vehicles
        self.update_M(next_location)
        print(f"Picked location {next_location} with projected flow {self.location_flows[next_location]}")

    def update_M(self, picked_location):
        location_vehicle = self.pmcpBParser.location_vehicles[picked_location]
        for vehicle in location_vehicle:
            if vehicle in self.pmcpBParser.vehicle_paths:
                self.pmcpBParser.vehicle_paths.pop(vehicle)
        self.M = self.generate_M(self.pmcpBParser.vehicle_paths)

    def generate_M(self, vehicle_paths):
        new_M = np.zeros((self.grid_size, self.grid_size), dtype=int)  # Reset the matrix
        for vehicle_id, path in vehicle_paths.items():
            for cell in path:
                new_M[cell[0], cell[1]] += 1
        return new_M
