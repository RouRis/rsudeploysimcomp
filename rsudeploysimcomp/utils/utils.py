import os

import numpy as np
import yaml


def load_config(env):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "app_config_" + env + ".yaml")
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


def adjust_coordinates_with_offsets(sumoparser, location):
    # Adjust the coordinates with the offsets
    adjusted_center_x = location[0] - sumoparser.x_offset
    adjusted_center_y = location[1] - sumoparser.y_offset

    return adjusted_center_x, adjusted_center_y
