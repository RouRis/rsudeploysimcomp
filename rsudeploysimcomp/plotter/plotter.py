import matplotlib.pyplot as plt  # Importing Matplotlib for plotting
import pandas as pd
import os
import json

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface
from rsudeploysimcomp.utils.utils import *


def plot():
    # Define the file pattern for your JSON files
    file_pattern = './Results/*.json'

    # Collect data by algorithm
    data_by_algorithm = collect_data(file_pattern)
    # Plot the data for each algorithm
    plot_coverage_by_algorithm_over_num_rsus(data_by_algorithm)
    plot_avg_distance_by_algorithm_over_num_rsus(data_by_algorithm)

    plot_coverage_by_algorithm_over_rsu_radius(data_by_algorithm)
    plot_avg_distance_by_algorithm_over_rsu_radius(data_by_algorithm)


def plot_coverage_by_algorithm_over_num_rsus(data_by_algorithm):
    plt.figure(figsize=(12, 8))
    for algorithm, data in data_by_algorithm.items():
        plt.plot(data['num_rsus'], data['coverage'], marker='o', linestyle='-', label=algorithm)
    plt.xlabel('Number of RSUs')
    plt.ylabel('Coverage (%)')
    plt.title('Coverage vs. Number of RSUs by Algorithm')
    plt.legend()
    plt.grid(True)
    plt.savefig("./Plots/Coverage_over_NUM_RSU.png")
    plt.show()


def plot_avg_distance_by_algorithm_over_num_rsus(data_by_algorithm):
    plt.figure(figsize=(12, 8))
    for algorithm, data in data_by_algorithm.items():
        plt.plot(data['num_rsus'], data['avg_distance'], marker='o', linestyle='-', label=algorithm)
    plt.xlabel('Number of RSUs')
    plt.ylabel('Average Distance')
    plt.title('Average Distance vs. Number of RSUs by Algorithm')
    plt.legend()
    plt.grid(True)
    plt.savefig("./Plots/Avg_Distance_over_NUM_RSU.png")
    plt.show()


def plot_coverage_by_algorithm_over_rsu_radius(data_by_algorithm):
    plt.figure(figsize=(12, 8))
    for algorithm, data in data_by_algorithm.items():
        plt.plot(data['rsu_radius'], data['coverage'], marker='o', linestyle='-', label=algorithm)
    plt.xlabel('RSU Radius')
    plt.ylabel('Coverage (%)')
    plt.title('Coverage vs. RSU Radius by Algorithm')
    plt.legend()
    plt.grid(True)
    plt.savefig("./Plots/Coverage_over_RSU_Radius.png")
    plt.show()


def plot_avg_distance_by_algorithm_over_rsu_radius(data_by_algorithm):
    plt.figure(figsize=(12, 8))
    for algorithm, data in data_by_algorithm.items():
        plt.plot(data['rsu_radius'], data['avg_distance'], marker='o', linestyle='-', label=algorithm)
    plt.xlabel('RSU Radius')
    plt.ylabel('Average Distance')
    plt.title('Average Distance vs. RSU Radius by Algorithm')
    plt.legend()
    plt.grid(True)
    plt.savefig("./Plots/Avg_Distance_over_RSU_Radius.png")
    plt.show()


class Plotter:
    def __init__(self, all_junctions):
        print("Plotter Initialization...\n")
        self.all_junctions = all_junctions
        self.rsu_sim_interface = RSU_SIM_Interface()

    def run(self, algorithm_name, rsu_positions, coverage, avg_distance, save_path=None):
        self.plot_deployment_map(rsu_positions, algorithm_name, coverage, avg_distance, save_path)
        self.collect_coverage_data(algorithm_name, coverage, avg_distance)
        # self.plot_histo_shortest_distance_overall(algorithm_name)
        # self.plot_histo_avg_distance_per_timestep(algorithm_name)
        # self.plot_histo_coverage_per_timestep(algorithm_name)

    def plot_histo_avg_distance_per_timestep(self, algorithm_name):
        relevant_data = self.rsu_sim_interface.parse_relevant_data()
        # Step 1: Group by time_step and calculate the average distance
        avg_distance_per_timestep = relevant_data.groupby("time_step")["distance"].mean()
        # Step 2: Plot a histogram of the average distances
        plt.figure(figsize=(10, 6))
        plt.hist(avg_distance_per_timestep, bins=50, edgecolor="black")
        plt.title("Histogram of Average Distances per Time Step - " + algorithm_name)
        plt.xlabel("Average Distance")
        plt.ylabel("Frequency")
        plt.show()

    def plot_histo_coverage_per_timestep(self, algorithm_name):
        relevant_data = self.rsu_sim_interface.parse_relevant_data()
        # Step 2: Determine coverage - filter data based on RSU radius
        relevant_data["within_coverage"] = relevant_data["distance"] <= self.rsu_sim_interface.rsu_radius

        # Step 3: Calculate coverage percentage per RSU per time step
        coverage_per_timestep_rsu = relevant_data.groupby(["time_step"])["within_coverage"].mean() * 100

        # Optional: You might want to average this across RSUs to get a general view per timestep
        coverage_per_timestep = coverage_per_timestep_rsu.groupby("time_step").mean()

        plt.figure(figsize=(10, 6))
        plt.hist(coverage_per_timestep, bins=30, edgecolor="black")
        plt.title("Histogram of RSU Coverage Percentage per Time Step - " + algorithm_name)
        plt.xlabel("Coverage Percentage")
        plt.ylabel("Frequency")
        plt.show()

    def plot_histo_shortest_distance_overall(self, algorithm_name):
        relevant_data = self.rsu_sim_interface.parse_relevant_data()
        # Step 2: Plot a histogram of all distances
        plt.figure(figsize=(10, 6))
        plt.hist(relevant_data['distance'], bins=30, edgecolor='black')
        plt.title("Histogram of Distances - " + algorithm_name)
        plt.xlabel('Distance')
        plt.ylabel('Frequency')
        plt.show()

    def collect_coverage_data(self, algorithm_name, coverage, avg_distance):
        """
        Collect coverage data for each simulation run to be used for aggregated plotting.
        """
        rsu_radius = self.rsu_sim_interface.rsu_radius
        num_rsus = self.rsu_sim_interface.num_rsus

        relevant_data = self.rsu_sim_interface.parse_relevant_data()

        # Step 2: Determine coverage - filter data based on RSU radius
        relevant_data["within_coverage"] = relevant_data["distance"] <= rsu_radius

        # Step 3: Calculate coverage percentage per RSU per time step
        coverage_per_timestep_rsu = relevant_data.groupby(["time_step"])["within_coverage"].mean() * 100

        # Average this across RSUs to get a general view per timestep
        coverage_per_timestep = coverage_per_timestep_rsu.groupby("time_step").mean()

        coverage_per_timestep_list = coverage_per_timestep.tolist()

        # Prepare the data to be saved
        data_to_save = {
            "algorithm": algorithm_name,
            "num_rsus": num_rsus,
            "rsu_radius": rsu_radius,
            "coverage": coverage,
            "avg_distance": avg_distance,
            "coverage_per_timestep": coverage_per_timestep_list
        }

        serializable_data = convert_to_serializable(data_to_save)

        results_dir = "Results"

        # Create the directory for results if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)

        # Construct the file path for the JSON file
        file_path = os.path.join(results_dir, f"{algorithm_name}_{num_rsus}_{rsu_radius}.json")

        # Save the data to a JSON file
        with open(file_path, 'w') as f:
            json.dump(serializable_data, f, indent=4)

        print(f"Coverage data for {algorithm_name} with {num_rsus} RSUs saved to {file_path}")

    def plot_deployment_map(self, rsu_positions, title, coverage, avg_distance, save_path=None):
        config = load_config()

        fcd_path = (
                config["general"]["base_path"]
                + config["rsu_interface"]["input_path"]
                + config["rsu_interface"]["scenario"]
                + config["rsu_interface"]["fcd_parquet"]
        )

        # Plot Junctions
        rsu_positions_x = [coord[0] for coord in rsu_positions]
        rsu_positions_y = [coord[1] for coord in rsu_positions]

        # Plot Junctions
        all_junctions_x = [coord[0] for coord in self.all_junctions]
        all_junctions_y = [coord[1] for coord in self.all_junctions]

        df = pd.read_parquet(fcd_path)
        plt.figure(figsize=(10, 8))
        plt.plot(
            df["x"],
            df["y"],
            linestyle="-",
            color="gray",
            marker="o",
            markersize=1,
            linewidth=0.0001,
            label="Street Network",
        )
        plt.scatter(all_junctions_x, all_junctions_y, color="blue", s=1, marker="o", label="Junctions")
        plt.scatter(
            rsu_positions_x, rsu_positions_y, color="red", s=100, marker="*", label="RSU Locations", zorder=5
        )
        plt.legend(loc="best")
        plt.xlabel("X Coordinates")
        plt.ylabel("Y Coordinates")
        plt.title(title)
        plt.grid(True)

        # Add metrics outside the plot area, just above the title
        metrics_text = f"Coverage: {coverage:.2f}%\nAvg Distance: {avg_distance:.2f}m"
        plt.gcf().text(
            0.3,
            0.95,
            metrics_text,
            fontsize=12,
            horizontalalignment="center",
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7),
        )

        if save_path:
            plt.savefig(save_path)
            print(f"Plot of Deployment-Map saved to {save_path}")
        else:
            plt.show()
