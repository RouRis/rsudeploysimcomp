import os

import matplotlib.pyplot as plt  # Importing Matplotlib for plotting
import numpy as np
import pandas as pd
import yaml


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


def plot_deployment(picked_junctions, title):
    config = load_config()

    fcd_path = (
        config["general"]["base_path"]
        + config["rsu_interface"]["input_path"]
        + config["rsu_interface"]["scenario"]
        + config["rsu_interface"]["fcd_parquet"]
    )

    # Plot Junctions
    junctions_x = [coord[0] for coord in picked_junctions]
    junctions_y = [coord[1] for coord in picked_junctions]

    df = pd.read_parquet(fcd_path)
    plt.figure(figsize=(10, 8))
    plt.plot(
        df["x"],
        df["y"],
        linestyle="-",
        color="gray",
        marker="o",
        markersize=1,
        linewidth=0.001,
        label="Street Network",
    )
    plt.scatter(junctions_x, junctions_y, color="blue", s=50, marker="*", label="RSU Locations")
    plt.legend()
    plt.xlabel("X Coordinates")
    plt.ylabel("Y Coordinates")
    plt.title(title)
    plt.grid(True)

    plt.show()
