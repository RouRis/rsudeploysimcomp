from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface, generate_deployment_file, \
    run_pipeline
from rsudeploysimcomp.utils.utils import load_config
import time


class AllJunctions:
    def __init__(self, sumoparser):
        print("AllJunctions Initialization & Run...\n")
        self.config = load_config()
        self.name = "AllJunctions"
        self.sumoparser = sumoparser
        self.rsu_sim_interface = RSU_SIM_Interface()
        self.coverage = -1
        self.avg_distance = -1
        self.picked_junctions = None
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
        self.run()

    def run(self):
        self.picked_junctions = [
            (junction["x"] - self.sumoparser.x_offset, junction["y"] - self.sumoparser.y_offset)
            for junction in self.sumoparser.junctions
        ]
        self.coverage, self.avg_distance = run_pipeline(algorithm_name=self.name,
                                                        picked_junctions=self.picked_junctions,
                                                        deployment_csv_path=self.deployment_csv_path,
                                                        deployment_parquet_path=self.deployment_parquet_path,
                                                        rsu_sim_interface=self.rsu_sim_interface)
