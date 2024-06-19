# Init Set of all locations (all_locations)
# Init Empty Set of picked locations (picked_locations)
# Init RSU Counter
# Define FlowProjection Method
# First iteration: Location with highest Vehicle Number
# After: See Paper
#Alg: While-loop over projection flow and picking the highest projection
#Return the picked_locations

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix


class PMCB_P:
    def __init__(self, M, P, grid_size, max_rsus):
        self.grid_size = grid_size  # Number of cells per dimension
        self.M = M  # 2D array with vehicle counts
        self.P = P  # 2D array (sparsed) with migration ratios between locations
        self.max_rsus = max_rsus  # Maximum number of RSUs to be deployed
        self.location_flows = np.zeros((self.grid_size, self.grid_size))
        self.remaining_locations = set((x, y) for x in range(grid_size) for y in range(grid_size))
        self.picked_locations = set()
        self.rsu_counter = 0
        self.run()

    def run(self):
        while self.rsu_counter <= self.max_rsus:
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

    def pick_next_location(self):
        # Find the location with the highest projected flow
        next_location = np.unravel_index(np.argmax(self.location_flows, axis=None), self.location_flows.shape)

        # Add the best location to picked_locations and remove from all_locations
        self.picked_locations.add(next_location)
        self.remaining_locations.remove(next_location)
        print(f"Picked location {next_location} with projected flow {self.location_flows[next_location]}")



# When reading the xml: Create list (whatever?) of locations as well as vehicles. Store for every location the visiting vehicles
# and for every vehicle the visited locations. With those information you can delete the vehicles during flow_projection of the model (as wanted by algorithm)