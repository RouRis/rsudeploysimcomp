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

    plot_exec_time_pipeline(
        in_file="ExecTime/Pipeline/pipeline_exec_time.csv",
        out_file="Plots/ExecTime/pipeline_exec_time.pdf",
    )
    plot_exec_time_algorithm(
        in_file="ExecTime/Algorithms/algorithms_exec_time.csv",
        out_file="Plots/ExecTime/algorithms_exec_time.pdf",
    )
    plot_best_solutions(
        in_file="best_solutions.csv",
        out_file="Plots/GARSUD/best_solutions.pdf",
    )


def plot_coverage_by_algorithm_over_num_rsus(data_by_num_rsus, rsu_radius_wanted, grid_size):
    # Define a dictionary with fixed colors for each algorithm
    algorithm_colors = {
        "Density-Based": "green",  # Sort this alphabetically
        "GARSUD": "blue",
        "PMCP_B": "red",
    }

    plt.figure(figsize=(12, 8))

    # Store data for plotting in a list so that we can ensure alphabetical order
    plot_data = []

    for (algorithm, rsu_radius), data in data_by_num_rsus.items():
        if rsu_radius_wanted == rsu_radius:
            color = algorithm_colors.get(algorithm, "black")  # Default to black if algorithm not in dictionary
            plot_data.append((algorithm, data, color))

    # Sort the plot data by algorithm name alphabetically
    plot_data.sort(key=lambda x: x[0])

    # Plot each algorithm's data after sorting alphabetically
    for algorithm, data, color in plot_data:
        plt.plot(
            data["num_rsus"],
            data["coverage"],
            marker="o",
            linestyle="-",
            linewidth=3,  # Increase line thickness
            label=f"{algorithm}",  # Only algorithm name in the legend
            color=color,
        )

    # Set axis limits as requested
    plt.xlim([0, 1050])
    plt.ylim([0, 100])  # Set y-axis from 0 to 100%

    # Increase font size for labels and titles
    plt.xlabel("Number of RSUs", fontsize=16)
    plt.ylabel("Coverage (%)", fontsize=16)
    plt.title("Coverage vs. Number of RSUs", fontsize=16)

    plt.tick_params(axis="both", which="major", labelsize=16)

    # Increase the font size of the legend and display it
    plt.legend(fontsize=12)

    # Add grid for easier interpretation of the plot
    plt.grid(True)

    # Save the figure
    plt.savefig(f"./Plots/Coverage_over_NUM_RSU__radius{rsu_radius_wanted}_grid{grid_size}.pdf")


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
    plt.scatter(num_rsus, prep_disolv_time, color="blue", label="prep-disolv")
    plt.scatter(num_rsus, prep_link_time, color="green", label="link-disolv")
    plt.scatter(num_rsus, run_disolv_time, color="red", label="run-disolv")

    # Add titles and labels
    plt.title("Execution Times vs. Number of RSUs", fontsize=16)
    plt.xlabel("Number of RSUs", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=16)

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
    plt.title("Execution Time vs. Number of RSUs for Different Algorithms and RSU Radii", fontsize=16)
    plt.xlabel("Number of RSUs", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.legend()

    # Save the plot to the output file
    plt.savefig(out_file)


def plot_best_solutions(in_file, out_file):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(in_file)

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(df["Generation"], df["Best Solution"], marker="o", color="b", linestyle="-", markersize=4)
    plt.title("Best Solution Over Generations", fontsize=16)
    plt.xlabel("Generation", fontsize=16)
    plt.ylabel("Best Solution Coverage (%)", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(out_file)


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
