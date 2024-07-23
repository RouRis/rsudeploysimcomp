from rsudeploysimcomp.utils.utils import adjust_coordinates_with_offsets, find_closest_junction


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
            rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)
            adjusted_center_x, adjusted_center_y = adjust_coordinates_with_offsets(self.sumoparser, rsu_location)
            self.picked_junctions.add((adjusted_center_x, adjusted_center_y))
