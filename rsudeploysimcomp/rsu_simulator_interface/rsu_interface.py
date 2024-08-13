import os

import pandas as pd
import subprocess

from rsudeploysimcomp.utils.utils import load_config


class RSU_SIM_Interface:

    def __init__(self):
        self.config = load_config()

    def export_picked_locations_to_csv(self, file_path, junctions):
        data = list(junctions)
        agent_ids = [200000 + i for i in range(len(junctions))]
        time_steps = [0] * len(junctions)
        df = pd.DataFrame(
            {
                "time_step": time_steps,
                "agent_id": agent_ids,
                "x": [coord[0] for coord in data],
                "y": [coord[1] for coord in data],
            }
        )
        df.to_csv(file_path, index=False)

    def convert_csv_to_parquet(self, csv_file_path, parquet_file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        # Convert the DataFrame to Parquet format
        df.to_parquet(parquet_file_path, index=False)

    def get_metrics_from_simulator(self):
        tx_data_parquet_path = (self.config["general"]["base_path"]
                                + self.config["rsu_interface"]["output_path"]
                                + self.config["rsu_interface"]["scenario"]
                                + "/tx_data.parquet")

        return self.parse_output_file(tx_data_parquet_path)

    def parse_output_file(self, parquet_file_path, reach_distance=1000):
        # Read the Parquet file into a DataFrame
        df = pd.read_parquet(parquet_file_path)

        relevant_data = df[df["agent_id"] < 200000]
        relevant_data = relevant_data[relevant_data["selected_agent"] >= 200000]

        # Filter rows where the distance is within the reach of the RSU
        covered = relevant_data[relevant_data["distance"] <= reach_distance]

        # Total number of car records (agent_id > 0)
        total_car_records = len(relevant_data)

        # Number of covered car records
        covered_car_records = len(covered)

        # Calculate the coverage percentage
        coverage_percentage = (covered_car_records / total_car_records) * 100 if total_car_records > 0 else 0

        average_distance = relevant_data["distance"].mean() if total_car_records > 0 else float("nan")

        return coverage_percentage, average_distance

    def generate_deployment_file(self, junctions, csv_path, parquet_path):
        self.export_picked_locations_to_csv(csv_path, junctions)
        self.convert_csv_to_parquet(csv_path, parquet_path)

    def prep_position_files(self, prep_disolv_path, configs_path):
        command = [
            prep_disolv_path + "/.venv/bin/python",
            prep_disolv_path + "/src/__main__.py",
            "--config",
            configs_path + "/positions.toml"
        ]

        self.run_command(command)
        print("Prep position files done")

    def prep_link_files(self, disolv_path, configs_path):
        command = [
            disolv_path + "/target/release/disolv-links",
            "--config",
            configs_path + "/links.toml"
        ]

        self.run_command(command)
        print("Prep link files done")

    def run_rsu_simulator(self, disolv_path, configs_path):
        command = [
            disolv_path + "/target/release/disolv-v2x",
            "--config",
            configs_path + "/disolv.toml"
        ]

        self.run_command(command)
        print("Run Simulator")


    def run_command(self, command):
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if an error occurred
        if result.returncode != 0:
            print("Error executing the command:")
            print("stderr:", result.stderr)
            print("stdout:", result.stdout)  # Optional, if stdout is also relevant
            print("Return code:", result.returncode)

    def trigger_rsu_simulator(self):
        base_path = self.config["general"]["base_path"]
        prep_disolv_path = base_path + self.config["rsu_interface"]["prep_disolv_path"]
        disolv_path = base_path + self.config["rsu_interface"]["disolv_path"]
        configs_path = (base_path
                        + self.config["rsu_interface"]["configs_path"]
                        + self.config["rsu_interface"]["scenario"])

        self.prep_link_files(disolv_path, configs_path)
        self.prep_position_files(prep_disolv_path, configs_path)
        self.run_rsu_simulator(disolv_path, configs_path)
