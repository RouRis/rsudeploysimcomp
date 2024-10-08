import csv
import subprocess
import time

import pandas as pd

from rsudeploysimcomp.Utils.utils import load_config


def export_picked_locations_to_csv(file_path, junctions):
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


def convert_csv_to_parquet(csv_file_path, parquet_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert the DataFrame to Parquet format
    df.to_parquet(parquet_file_path, index=False)


def generate_deployment_file(junctions, csv_path, parquet_path):
    export_picked_locations_to_csv(csv_path, junctions)
    convert_csv_to_parquet(csv_path, parquet_path)


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    # Check if an error occurred
    if result.returncode != 0:
        print("Error executing the command:")
        print("stderr:", result.stderr)
        print("stdout:", result.stdout)  # Optional, if stdout is also relevant
        print("Return code:", result.returncode)


def prep_position_files(prep_disolv_path, configs_path):
    command = [
        prep_disolv_path + "/.venv/bin/python",
        prep_disolv_path + "/src/__main__.py",
        "--config",
        configs_path + "/positions.toml",
    ]
    run_command(command)
    # print("Prep position files done")


def prep_link_file(disolv_path, configs_path):
    command = [disolv_path + "/target/release/disolv-links", "--config", configs_path + "/links.toml"]
    run_command(command)
    # print("Prep link files done")


def run_rsu_simulator(disolv_path, configs_path):
    command = [disolv_path + "/target/release/disolv-v2x", "--config", configs_path + "/disolv.toml"]
    run_command(command)
    # print("Run Simulator")


def run_pipeline(
    picked_junctions, deployment_csv_path, deployment_parquet_path, rsu_sim_interface, algorithm_name
):
    generate_deployment_file(picked_junctions, deployment_csv_path, deployment_parquet_path)
    rsu_sim_interface.trigger_rsu_simulator(algorithm_name)
    return rsu_sim_interface.get_metrics_from_simulator()


class VanetSimulatorInterface:
    def __init__(self):
        self.config = load_config()
        self.rsu_radius = self.config["General"]["rsu_radius"]
        self.num_rsus = self.config["General"]["num_rsus"]
        self.grid_size = self.config["General"]["grid_size"]
        self.tx_data_parquet_path = (
            self.config["General"]["base_path"]
            + self.config["VanetInterface"]["output_path"]
            + self.config["VanetInterface"]["scenario"]
            + "/tx_data.parquet"
        )

    def parse_relevant_data(self):
        # Read the Parquet file into a DataFrame
        # But only relevant Data: where link-sender is a vehicle, and link-receiver is a rsu
        df = pd.read_parquet(self.tx_data_parquet_path)

        relevant_data = df[df["agent_id"] < 200000]
        relevant_data = relevant_data[relevant_data["selected_agent"] >= 200000]

        return relevant_data

    def parse_coverage_and_avg_distance(self, rsu_radius=1000):
        relevant_data = self.parse_relevant_data()

        # Filter rows where the distance is within the reach of the RSU
        covered = relevant_data[relevant_data["distance"] <= rsu_radius]

        # Total number of car records (agent_id > 0)
        total_car_records = len(relevant_data)

        # Number of covered car records
        covered_car_records = len(covered)

        # Calculate the coverage percentage
        coverage_percentage = (covered_car_records / total_car_records) * 100 if total_car_records > 0 else 0

        average_distance = relevant_data["distance"].mean() if total_car_records > 0 else float("nan")

        return coverage_percentage, average_distance

    def get_metrics_from_simulator(self):
        return self.parse_coverage_and_avg_distance(rsu_radius=self.rsu_radius)

    def trigger_with_time_tracking(
        self, prep_disolv_path, disolv_path, configs_path, csv_file_path, algorithm_name
    ):
        # 1 - prep-disolv (prepare positions file)
        start_segment_time_pipe = time.perf_counter()
        prep_position_files(prep_disolv_path, configs_path)
        end_segment_time_pipe = time.perf_counter()
        prep_disolv_time = end_segment_time_pipe - start_segment_time_pipe

        # 2 - disolv (prepare link file)
        start_segment_time_pipe = time.perf_counter()
        prep_link_file(disolv_path, configs_path)
        end_segment_time_pipe = time.perf_counter()
        prep_link_time = end_segment_time_pipe - start_segment_time_pipe

        # 3 - run disolv
        start_segment_time_pipe = time.perf_counter()
        run_rsu_simulator(disolv_path, configs_path)
        end_segment_time_pipe = time.perf_counter()
        run_disolv_time = end_segment_time_pipe - start_segment_time_pipe

        with open(csv_file_path, "a", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the header if the file is empty
            if csvfile.tell() == 0:
                csv_writer.writerow(
                    [
                        "prep_disolv_time",
                        "prep_link_time",
                        "run_disolv_time",
                        "num_rsus",
                        "rsu_radius",
                        "grid_size",
                        "algorithm",
                    ]
                )
            csv_writer.writerow(
                [
                    prep_disolv_time,
                    prep_link_time,
                    run_disolv_time,
                    self.num_rsus,
                    self.rsu_radius,
                    self.grid_size,
                    algorithm_name,
                ]
            )

    def trigger(self, prep_disolv_path, disolv_path, configs_path):
        # 1 - prep-disolv (prepare positions file)
        prep_position_files(prep_disolv_path, configs_path)
        # 2 - disolv (prepare link file)
        prep_link_file(disolv_path, configs_path)
        # 3 - run disolv
        run_rsu_simulator(disolv_path, configs_path)

    def trigger_rsu_simulator(self, algorithm_name):
        base_path = self.config["General"]["base_path"]
        prep_disolv_path = base_path + self.config["VanetInterface"]["prep_disolv_path"]
        disolv_path = base_path + self.config["VanetInterface"]["disolv_path"]
        configs_path = (
            base_path + self.config["VanetInterface"]["configs_path"] + self.config["VanetInterface"]["scenario"]
        )
        csv_file_path_run_exec_time = "ExecTime/Pipeline/pipeline_exec_time.csv"

        track_execution_time = bool(self.config["VanetInterface"]["track_execution_time"])
        if track_execution_time:
            self.trigger_with_time_tracking(
                prep_disolv_path=prep_disolv_path,
                disolv_path=disolv_path,
                configs_path=configs_path,
                csv_file_path=csv_file_path_run_exec_time,
                algorithm_name=algorithm_name,
            )
        else:
            self.trigger(prep_disolv_path=prep_disolv_path, disolv_path=disolv_path, configs_path=configs_path)
