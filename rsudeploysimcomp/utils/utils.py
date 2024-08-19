import os

import matplotlib.pyplot as plt  # Importing Matplotlib for plotting
import numpy as np
import pandas as pd
import yaml
from math import sqrt


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "app_config" + ".yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def find_closest_junction(sumoparser, center_x, center_y):
    closest_junction = None
    min_distance = float("inf")
    for junction in sumoparser.junctions:
        distance = np.sqrt((center_x - junction["x"]) ** 2 + (center_y - junction["y"]) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_junction = (junction["x"], junction["y"])
    return closest_junction


def adjust_coordinates_by_offsets(sumoparser, location):
    # Adjust the coordinates by offsets
    adjusted_center_x = location[0] - sumoparser.x_offset
    adjusted_center_y = location[1] - sumoparser.y_offset

    return adjusted_center_x, adjusted_center_y


def new_location_is_within_reach(new_location, picked_junctions, rsu_radius):
    """
    Check if the new location is within the reach of any already selected RSU.
    """
    for existing_location in picked_junctions:
        distance = sqrt((new_location[0] - existing_location[0]) ** 2 +
                        (new_location[1] - existing_location[1]) ** 2)
        if distance <= rsu_radius:
            return True
    return False


class Plotter:
    def __init__(self, all_junctions):
        self.all_junctions = all_junctions

    def plot_deployment(self, rsu_positions, title, coverage, avg_distance, save_path=None):
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
        plt.scatter(rsu_positions_x, rsu_positions_y, color="red", s=100, marker="*", label="RSU Locations", zorder=5)
        plt.legend(loc='best')
        plt.xlabel("X Coordinates")
        plt.ylabel("Y Coordinates")
        plt.title(title)
        plt.grid(True)

        # Add metrics outside the plot area, just above the title
        metrics_text = f"Coverage: {coverage:.2f}%\nAvg Distance: {avg_distance:.2f}m"
        plt.gcf().text(0.3, 0.95, metrics_text, fontsize=12, horizontalalignment='center', verticalalignment='top',
                       bbox=dict(facecolor='white', alpha=0.7))

        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
