from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface, generate_deployment_file, \
    run_pipeline
from rsudeploysimcomp.utils.utils import (
    adjust_coordinates_by_offsets,
    find_closest_junction,
    load_config,
    new_location_is_within_reach,
)


class DensityBased:
    def __init__(self, sumoparser):
        print("DensityBased Initialization...\n")

        self.config = load_config()
        self.name = "DensityBased"
        self.rsu_radius = self.config["general"]["rsu_radius"]
        self.num_rsus = self.config["general"]["num_rsus"]
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
        self.sumoparser = sumoparser
        self.rsu_sim_interface = RSU_SIM_Interface()
        self.grid_size = sumoparser.grid_size
        self.coverage = -1
        self.avg_distance = -1
        self.M = sumoparser.M
        self.picked_junctions = set()
        self.covered_junctions = set()

    def run(self):
        """
        Runs the RSU deployment algorithm by selecting locations based on vehicle density.
        """
        # Convert the matrix M into a list of (x, y, density) tuples
        density_list = [(x, y, self.M[x, y]) for x in range(self.grid_size) for y in range(self.grid_size)]
        # Sort the list by density in descending order
        density_list.sort(key=lambda item: item[2], reverse=True)

        # Pick the top locations based on vehicle density
        for i in range(len(density_list)):
            if len(self.picked_junctions) >= self.num_rsus:
                break

            x, y, _ = density_list[i]
            # Get the junction closest to the center of the grid cell
            center_x = (x + 0.5) * (self.sumoparser.x_max / self.grid_size)
            center_y = (y + 0.5) * (self.sumoparser.y_max / self.grid_size)
            rsu_location = find_closest_junction(self.sumoparser, center_x, center_y)
            adjusted_center_x, adjusted_center_y = adjust_coordinates_by_offsets(self.sumoparser, rsu_location)
            # Check if the location is within the reach of any already picked RSU
            if not new_location_is_within_reach(
                (adjusted_center_x, adjusted_center_y), self.picked_junctions, self.rsu_radius
            ):
                self.picked_junctions.add((adjusted_center_x, adjusted_center_y))

        self.coverage, self.avg_distance = run_pipeline(algorithm_name=self.name,
                                                        picked_junctions=self.picked_junctions,
                                                        deployment_csv_path=self.deployment_csv_path,
                                                        deployment_parquet_path=self.deployment_parquet_path,
                                                        rsu_sim_interface=self.rsu_sim_interface)
