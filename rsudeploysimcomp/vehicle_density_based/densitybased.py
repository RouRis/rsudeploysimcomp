import numpy as np


class DensityBased:
    def __init__(self, sumoparser, max_rsus):
        self.max_rsus = max_rsus
        self.sumoparser = sumoparser
        self.grid_size = sumoparser.grid_size
        self.M = sumoparser.M
        self.picked_junctions = set()
        self.run()

    def run(self):
        """
        Runs the RSU deployment algorithm by selecting locations based on vehicle density.
        """
        # Convert the matrix M into a list of (x, y, density) tuples
        density_list = [(x, y, self.M[x, y]) for x in range(self.grid_size) for y in range(self.grid_size)]
        # Sort the list by density in descending order
        density_list.sort(key=lambda item: item[2], reverse=True)

        # Pick the top locations based on vehicle density
        for i in range(min(self.max_rsus, len(density_list))):
            x, y, _ = density_list[i]
            # Get the junction closest to the center of the grid cell
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            closest_junction = self.find_closest_junction(center_x, center_y)

            self.picked_junctions.add(closest_junction)

    def find_closest_junction(self, center_x, center_y):
        closest_junction = None
        min_distance = float("inf")
        for junction in self.sumoparser.junctions:
            distance = np.sqrt((center_x - junction["x"]) ** 2 + (center_y - junction["y"]) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_junction = (junction["x"], junction["y"])
        return closest_junction
