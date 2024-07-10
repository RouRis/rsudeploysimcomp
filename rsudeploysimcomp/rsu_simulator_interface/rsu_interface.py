import pandas as pd


class RsuDeployment:
    def __init__(self, sumo_parser, max_rsus):
        self.sumo_parser = sumo_parser
        self.max_rsus = max_rsus
        self.grid_size = self.sumo_parser.grid_size
        self.M = self.sumo_parser.generate_matrix_m_with_vehicle_paths()
        self.remaining_locations = set((x, y) for x in range(self.grid_size) for y in range(self.grid_size))
        self.picked_locations = set()
        self.run()

    def run(self):
        density_list = [(x, y, self.M[x, y]) for x in range(self.grid_size) for y in range(self.grid_size)]
        density_list.sort(key=lambda item: item[2], reverse=True)

        for i in range(min(self.max_rsus, len(density_list))):
            x, y, _ = density_list[i]
            self.picked_locations.add((x, y))
            self.remaining_locations.remove((x, y))

    def get_picked_locations(self):
        return self.picked_locations

    def export_picked_locations_to_csv(self, file_path):
        data = list(self.picked_locations)
        df = pd.DataFrame(data, columns=["x", "y"])
        df.to_csv(file_path, index=False)
