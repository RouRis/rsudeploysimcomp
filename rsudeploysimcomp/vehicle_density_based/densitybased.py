class DensityBased:
    def __init__(self, sumoparser, max_rsus):
        self.max_rsus = max_rsus
        self.grid_size = sumoparser.grid_size
        self.M = sumoparser.M
        self.picked_locations = set()
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
            self.picked_locations.add((x, y))
