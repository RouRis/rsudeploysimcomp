from rsudeploysimcomp.Utils.utils import load_config
from rsudeploysimcomp.VanetSimulatorInterface.vanet_sim_interface import VanetSimulatorInterface, run_pipeline


class AllJunctions:
    def __init__(self, sumoparser):
        print("AllJunctions Initialization & Run...\n")
        self.config = load_config()
        self.name = "AllJunctions"
        self.sumoparser = sumoparser
        self.vanet_simulator_interface = VanetSimulatorInterface()
        self.coverage = -1
        self.avg_distance = -1
        self.picked_junctions = None
        self.deployment_csv_path = (
            self.config["General"]["base_path"]
            + self.config["VanetInterface"]["input_path"]
            + self.config["VanetInterface"]["scenario"]
            + self.config["VanetInterface"]["deployment_csv_path"]
        )

        self.deployment_parquet_path = (
            self.config["General"]["base_path"]
            + self.config["VanetInterface"]["input_path"]
            + self.config["VanetInterface"]["scenario"]
            + self.config["VanetInterface"]["deployment_parquet_path"]
        )
        self.run()

    def run(self):
        self.picked_junctions = [
            (junction["x"] - self.sumoparser.x_offset, junction["y"] - self.sumoparser.y_offset)
            for junction in self.sumoparser.junctions
        ]
        self.coverage, self.avg_distance = run_pipeline(
            picked_junctions=self.picked_junctions,
            deployment_csv_path=self.deployment_csv_path,
            deployment_parquet_path=self.deployment_parquet_path,
            rsu_sim_interface=self.vanet_simulator_interface,
        )
