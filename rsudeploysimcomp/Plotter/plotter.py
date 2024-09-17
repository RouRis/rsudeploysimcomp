import json
import os

import matplotlib.pyplot as plt  # Importing Matplotlib for plotting
import pandas as pd

from rsudeploysimcomp.Utils.utils import collect_data, convert_to_serializable, load_config
from rsudeploysimcomp.VanetSimulatorInterface.vanet_sim_interface import VanetSimulatorInterface


def plot(num_rsus_range, rsu_radius_range):
    # Define the file pattern for your JSON files
    config = load_config()
    file_pattern = "./Results/*.json"
    # Collect data by algorithm
    data_by_algorithm, data_by_num_rsus, data_by_rsu_radius = collect_data(file_pattern)
    for rsu_radius in rsu_radius_range:
        grid_size = config["RadiusGridsizeMapping"][rsu_radius]
        # Plot the data for each algorithm
        plot_coverage_by_algorithm_over_num_rsus(data_by_num_rsus, rsu_radius, grid_size)
    #    plot_avg_distance_by_algorithm_over_num_rsus(data_by_num_rsus, rsu_radius)

    # for num_rsus in num_rsus_range:
    #    plot_coverage_by_algorithm_over_rsu_radius(data_by_rsu_radius, num_rsus)
    #    plot_avg_distance_by_algorithm_over_rsu_radius(data_by_rsu_radius, num_rsus)

    plot_exec_time_pipeline(
        in_file="ExecTime/Pipeline/pipeline_exec_time.csv",
        out_file="Plots/ExecTime/pipeline_exec_time.pdf",
    )
    plot_exec_time_algorithm(
        in_file="ExecTime/Algorithms/algorithms_exec_time.csv",
        out_file="Plots/ExecTime/algorithms_exec_time.pdf",
    )


def plot_coverage_by_algorithm_over_num_rsus(data_by_num_rsus, rsu_radius_wanted, grid_size):
    plt.figure(figsize=(12, 8))
    for (algorithm, rsu_radius), data in data_by_num_rsus.items():
        if rsu_radius_wanted == rsu_radius:
            plt.plot(
                data["num_rsus"],
                data["coverage"],
                marker="o",
                linestyle="-",
                label=algorithm + " rsu_radius:" + str(rsu_radius_wanted),
            )

    plt.xlabel("Number of RSUs")
    plt.ylabel("Coverage (%)")
    plt.title("Coverage vs. Number of RSUs")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./Plots/Coverage_over_NUM_RSU__radius{rsu_radius_wanted}_grid{grid_size}.pdf")
    plt.show()


def plot_avg_distance_by_algorithm_over_num_rsus(data_by_num_rsus, rsu_radius_wanted):
    plt.figure(figsize=(12, 8))
    for (algorithm, rsu_radius), data in data_by_num_rsus.items():
        if rsu_radius_wanted == rsu_radius:
            plt.plot(
                data["num_rsus"],
                [abs(el) for el in data["avg_distance"]],
                marker="o",
                linestyle="-",
                label=algorithm + " rsu_radius:" + str(rsu_radius_wanted),
            )
    plt.xlabel("Number of RSUs")
    plt.ylabel("Average Distance")
    plt.title("Average Distance vs. Number of RSUs")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./Plots/Avg_Distance_over_NUM_RSU_with_radius_{rsu_radius_wanted}.pdf")
    plt.show()


def plot_coverage_by_algorithm_over_rsu_radius(data_by_algorithm, num_rsus_wanted):
    plt.figure(figsize=(12, 8))
    for (algorithm, num_rsus), data in data_by_algorithm.items():
        if num_rsus_wanted == num_rsus:
            plt.plot(
                data["rsu_radius"],
                data["coverage"],
                marker="o",
                linestyle="-",
                label=algorithm + " num_rsus:" + str(num_rsus_wanted),
            )
    plt.xlabel("RSU Radius")
    plt.ylabel("Coverage (%)")
    plt.title("Coverage vs. RSU Radius")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./Plots/Coverage_over_RSU_Radius_with_num_rsus_{num_rsus_wanted}.pdf")
    plt.show()


def plot_avg_distance_by_algorithm_over_rsu_radius(data_by_algorithm, num_rsus_wanted):
    plt.figure(figsize=(12, 8))
    for (algorithm, num_rsus), data in data_by_algorithm.items():
        if num_rsus_wanted == num_rsus:
            plt.plot(
                data["rsu_radius"],
                [abs(el) for el in data["avg_distance"]],
                marker="o",
                linestyle="-",
                label=algorithm + " num_rsus:" + str(num_rsus_wanted),
            )
    plt.xlabel("RSU Radius")
    plt.ylabel("Average Distance")
    plt.title("Average Distance vs. RSU Radius")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./Plots/Avg_Distance_over_RSU_Radius_with_num_rsus_{num_rsus_wanted}.pdf")
    plt.show()


def plot_coverage_per_timestep(file_path):
    # Step 1: Read the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Step 2: Extract the coverage per timestep data
    coverage_per_timestep = data["coverage_per_timestep"]

    # Step 3: Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(coverage_per_timestep, marker="o", linestyle="-", color="b")
    plt.xlabel("Time Step")
    plt.ylabel("Coverage (%)")
    plt.title("Coverage Over Time Steps")
    plt.grid(True)
    plt.show()


def plot_avg_distance_per_timestep(file_path):
    # Step 1: Read the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Step 2: Extract the average distance per timestep data
    avg_distance_per_timestep = data["avg_distance_per_timestep"]

    # Step 3: Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(avg_distance_per_timestep, marker="o", linestyle="-", color="r")
    plt.xlabel("Time Step")
    plt.ylabel("Average Distance")
    plt.title("Average Distance Over Time Steps")
    plt.grid(True)
    plt.show()


def plot_coverage_histogram(file_path):
    # Step 1: Read the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Step 2: Extract the coverage and average distance data
    coverage_per_timestep = data["coverage_per_timestep"]

    # Step 3: Plot the histogram
    plt.figure(figsize=(6, 6))
    plt.hist(coverage_per_timestep, bins=20, color="b", alpha=0.7)
    plt.xlabel("Coverage (%)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Coverage Over Time Steps")
    plt.grid(True)
    plt.show()


def plot_avg_distance_histogram(file_path):
    # Step 1: Read the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Step 2: Extract the coverage and average distance data
    avg_distance_per_timestep = data["avg_distance_per_timestep"]

    # Step 3: Plot the histogram
    plt.figure(figsize=(6, 6))
    plt.hist(avg_distance_per_timestep, bins=20, color="r", alpha=0.7)
    plt.xlabel("Average Distance")
    plt.ylabel("Frequency")
    plt.title("Histogram of Average Distance Over Time Steps")
    plt.grid(True)
    plt.show()


def plot_exec_time_pipeline(in_file, out_file):
    # Read the CSV file
    df = pd.read_csv(in_file)

    # Extract the columns for plotting
    num_rsus = df["num_rsus"]
    prep_disolv_time = df["prep_disolv_time"]
    prep_link_time = df["prep_link_time"]
    run_disolv_time = df["run_disolv_time"]

    # Plot the scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(num_rsus, prep_disolv_time, color="blue", label="Prep Disolv Time")
    plt.scatter(num_rsus, prep_link_time, color="green", label="Prep Link Time")
    plt.scatter(num_rsus, run_disolv_time, color="red", label="Run Disolv Time")

    # Add titles and labels
    plt.title("Execution Times vs. Number of RSUs")
    plt.xlabel("Number of RSUs")
    plt.ylabel("Execution Time (s)")
    plt.legend()

    # Show the plot
    plt.savefig(out_file)  # Change the filename and format as needed


def plot_exec_time_algorithm(in_file, out_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(in_file)

    # Create a scatter plot with different markers for each combination of algorithm and RSU radius
    plt.figure(figsize=(12, 8))

    # Group the data by 'algorithm' and 'rsu_radius'
    grouped = df.groupby(["algorithm", "rsu_radius"])

    # Define custom colors for each algorithm
    color_dict = {
        "PMCP_B": "red",  # PMCP_B in red
        "DensityBased": "green",  # Density-Based in green
        "GARSUD": "blue",  # GARSUD in blue
    }

    # Assign different markers for each group
    markers = ["o", "s", "D", "^", "v", "<", ">"]

    for i, ((algo, radius), subset) in enumerate(grouped):
        # Plot each group with the specified color and marker
        plt.scatter(
            subset["num_rsus"],
            subset["exec_time"],
            label=f"{algo} (Radius: {radius})",
            color=color_dict.get(algo, "black"),  # Default to black if algorithm is not in color_dict
            marker=markers[i % len(markers)],
        )

    # Add titles and labels
    plt.title("Execution Time vs. Number of RSUs for Different Algorithms and RSU Radii")
    plt.xlabel("Number of RSUs")
    plt.ylabel("Execution Time (s)")
    plt.legend()

    # Save the plot to the output file
    plt.savefig(out_file)

    # Show the plot
    plt.show()


def old_plot_exec_time_algorithm(in_file, out_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(in_file)

    # Create a scatter plot with different markers for each combination of algorithm and RSU radius
    plt.figure(figsize=(12, 8))

    # Group the data by 'algorithm' and 'rsu_radius'
    grouped = df.groupby(["algorithm", "rsu_radius"])

    # Assign different colors and markers for each group
    markers = ["o", "s", "D", "^", "v", "<", ">"]
    cmap = plt.get_cmap("viridis", len(grouped))  # Use 'viridis' colormap for distinct colors

    for i, ((algo, radius), subset) in enumerate(grouped):
        # Plot each group with different color and marker
        plt.scatter(
            subset["num_rsus"],
            subset["exec_time"],
            label=f"{algo} (Radius: {radius})",
            color=cmap(i),
            marker=markers[i % len(markers)],
        )

    # Add titles and labels
    plt.title("Execution Time vs. Number of RSUs for Different Algorithms and RSU Radii")
    plt.xlabel("Number of RSUs")
    plt.ylabel("Execution Time (s)")
    plt.legend()

    # Save the plot to the output file
    plt.savefig(out_file)

    # Show the plot
    plt.show()


class Plotter:
    def __init__(self):
        print("Plotter Initialization...\n")
        self.config = load_config()
        self.run_plot_deployment_map = bool(self.config["Plotter"]["run_plot_deployment_map"])
        self.all_junctions = None
        self.rsu_sim_interface = VanetSimulatorInterface()

    def run(self, algorithm_name, rsu_positions, coverage, avg_distance, save_path=None):
        if self.all_junctions is not None and self.run_plot_deployment_map:
            self.plot_deployment_map(rsu_positions, algorithm_name, coverage, avg_distance, save_path)
        self.collect_coverage_data(algorithm_name, coverage, avg_distance)

    def collect_coverage_data(self, algorithm_name, coverage, avg_distance):
        """
        Collect coverage data for each simulation run to be used for aggregated plotting.
        """
        rsu_radius = self.rsu_sim_interface.rsu_radius
        num_rsus = self.rsu_sim_interface.num_rsus
        grid_size = self.rsu_sim_interface.grid_size

        # Step 1: Parse relevant data from the RSU simulator interface
        relevant_data = self.rsu_sim_interface.parse_relevant_data()

        # Step 2: Determine coverage - filter data based on RSU radius
        relevant_data["within_coverage"] = relevant_data["distance"] <= rsu_radius

        # Step 3: Calculate coverage percentage per RSU per time step
        coverage_per_timestep_rsu = relevant_data.groupby(["time_step"])["within_coverage"].mean() * 100

        # Step 4: Calculate average distance per RSU per time step
        avg_distance_per_timestep_rsu = relevant_data.groupby("time_step")["distance"].mean()

        # Step 5: Average these across RSUs to get a general view per timestep
        coverage_per_timestep = coverage_per_timestep_rsu.groupby("time_step").mean()
        avg_distance_per_timestep = avg_distance_per_timestep_rsu.groupby("time_step").mean()

        # Convert these Series to lists for serialization
        coverage_per_timestep_list = coverage_per_timestep.tolist()
        avg_distance_per_timestep_list = avg_distance_per_timestep.tolist()

        if algorithm_name == "GARSUD":
            # Prepare the data to be saved
            data_to_save = {
                "algorithm": algorithm_name,
                "num_generations": self.config["Algorithms"]["GARSUD"]["num_generations"],
                "sol_per_pop": self.config["Algorithms"]["GARSUD"]["sol_per_pop"],
                "keep_parents": self.config["Algorithms"]["GARSUD"]["keep_parents"],
                "num_parents_mating": self.config["Algorithms"]["GARSUD"]["num_parents_mating"],
                "num_rsus": num_rsus,
                "rsu_radius": rsu_radius,
                "grid_size": grid_size,
                "coverage": coverage,
                "avg_distance": abs(avg_distance),
                "coverage_per_timestep": coverage_per_timestep_list,
                "avg_distance_per_timestep": avg_distance_per_timestep_list,
            }
        else:
            # Prepare the data to be saved
            data_to_save = {
                "algorithm": algorithm_name,
                "num_rsus": num_rsus,
                "rsu_radius": rsu_radius,
                "grid_size": grid_size,
                "coverage": coverage,
                "avg_distance": abs(avg_distance),
                "coverage_per_timestep": coverage_per_timestep_list,
                "avg_distance_per_timestep": avg_distance_per_timestep_list,
            }

        serializable_data = convert_to_serializable(data_to_save)

        results_dir = "Results"

        # Create the directory for results if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)

        # Construct the file path for the JSON file
        file_path = os.path.join(results_dir, f"{algorithm_name}_{num_rsus}_{rsu_radius}.json")

        # Save the data to a JSON file
        with open(file_path, "w") as f:
            json.dump(serializable_data, f, indent=4)

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
