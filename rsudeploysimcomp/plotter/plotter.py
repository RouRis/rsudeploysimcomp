import matplotlib.pyplot as plt  # Importing Matplotlib for plotting
import pandas as pd

from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface
from rsudeploysimcomp.utils.utils import load_config


class Plotter:
    def __init__(self, all_junctions):
        self.all_junctions = all_junctions
        self.rsu_sim_interface = RSU_SIM_Interface()

    def plot_histo_avg_distance_per_timestep(self):
        relevant_data = self.rsu_sim_interface.parse_relevant_data()
        # Step 1: Group by time_step and calculate the average distance
        avg_distance_per_timestep = relevant_data.groupby("time_step")["distance"].mean()
        # Step 2: Plot a histogram of the average distances
        plt.figure(figsize=(10, 6))
        plt.hist(avg_distance_per_timestep, bins=50, edgecolor="black")
        plt.title("Histogram of Average Distances per Time Step")
        plt.xlabel("Average Distance")
        plt.ylabel("Frequency")
        plt.show()

    def plot_histo_coverage_per_timestep(self):
        relevant_data = self.rsu_sim_interface.parse_relevant_data()
        # Step 2: Determine coverage - filter data based on RSU radius
        relevant_data["within_coverage"] = relevant_data["distance"] <= self.rsu_sim_interface.rsu_radius

        # Step 3: Calculate coverage percentage per RSU per time step
        coverage_per_timestep_rsu = relevant_data.groupby(["time_step"])["within_coverage"].mean() * 100

        # Optional: You might want to average this across RSUs to get a general view per timestep
        coverage_per_timestep = coverage_per_timestep_rsu.groupby("time_step").mean()

        plt.figure(figsize=(10, 6))
        plt.hist(coverage_per_timestep, bins=30, edgecolor="black")
        plt.title("Histogram of RSU Coverage Percentage per Time Step")
        plt.xlabel("Coverage Percentage")
        plt.ylabel("Frequency")
        plt.show()

    def plot_histo_shortest_distance_per_vehicle_per_timestep(self):
        pass

    def plot_histo_coverage_per_per_vehicle_timestep(self):
        pass

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
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
