import csv
import glob
import json
import os
import re
from math import sqrt

import numpy as np
import yaml


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "app_config" + ".yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_hyperparameter(config, name):
    """Get the param from the configuration."""
    # Extract the grid_size from the config
    param = config.get("General", {}).get(name, None)
    if param is None:
        raise ValueError("grid_size not found in configuration")

    # Check if grid_size is a list or a single integer
    if isinstance(param, int):
        # Return a list containing the single integer
        return [param]
    elif isinstance(param, list):
        # Return the list directly
        return param
    else:
        raise ValueError("grid_size must be an integer or a list of integers")


def update_config(num_rsus, rsu_radius, grid_size):
    """
    Update the configuration file with a new number of RSUs.
    """
    config_path = "./config/app_config.yaml"

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Update the number of RSUs
    config["General"]["num_rsus"] = num_rsus
    config["General"]["rsu_radius"] = rsu_radius
    config["General"]["grid_size"] = grid_size

    # Save the updated configuration
    with open(config_path, "w") as file:
        yaml.safe_dump(config, file)


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
        distance = sqrt(
            (new_location[0] - existing_location[0]) ** 2 + (new_location[1] - existing_location[1]) ** 2
        )
        if distance <= rsu_radius:
            return True
    return False


def convert_to_serializable(obj):
    """
    Helper function to convert non-serializable objects to a serializable format.
    """
    if isinstance(obj, np.float32) or isinstance(obj, np.float64):
        return float(obj)
    elif isinstance(obj, np.int32) or isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    return obj


def extract_data_from_result_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    algorithm = data.get("algorithm")
    num_rsus = data.get("num_rsus")
    coverage = data.get("coverage")
    avg_distance = data.get("avg_distance")
    rsu_radius = data.get("rsu_radius")

    return algorithm, num_rsus, rsu_radius, coverage, avg_distance


def track_algorithm_exec_time(start_segment_time, end_segment_time, algorithm):
    exec_time = end_segment_time - start_segment_time
    with open("ExecTime/Algorithms/algorithms_exec_time.csv", "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write the header if the file is empty
        if csvfile.tell() == 0:
            csv_writer.writerow(["exec_time", "num_rsus", "rsu_radius", "grid_size", "algorithm"])
        csv_writer.writerow(
            [exec_time, algorithm.num_rsus, algorithm.rsu_radius, algorithm.grid_size, algorithm.name]
        )


def sort_key(filename):
    # Extract the numerical part from the filename for sorting
    match = re.search(r"_(\d+)_\d+\.json$", filename)
    if match:
        return int(match.group(1))
    return 0


def collect_data(file_pattern):
    file_paths = sorted(glob.glob(file_pattern), key=sort_key)
    data_by_algorithm = {}
    data_by_num_rsus = {}
    data_by_rsu_radius = {}

    for path in file_paths:
        algorithm, num_rsus, rsu_radius, coverage, avg_distance = extract_data_from_result_json(path)

        if algorithm not in data_by_algorithm:
            data_by_algorithm[algorithm] = {"num_rsus": [], "rsu_radius": [], "coverage": [], "avg_distance": []}

        if (algorithm, rsu_radius) not in data_by_num_rsus:
            data_by_num_rsus[(algorithm, rsu_radius)] = {"num_rsus": [], "coverage": [], "avg_distance": []}

        if (algorithm, num_rsus) not in data_by_rsu_radius:
            data_by_rsu_radius[(algorithm, num_rsus)] = {"rsu_radius": [], "coverage": [], "avg_distance": []}

        data_by_algorithm[algorithm]["num_rsus"].append(num_rsus)
        data_by_algorithm[algorithm]["coverage"].append(coverage)
        data_by_algorithm[algorithm]["avg_distance"].append(avg_distance)
        data_by_algorithm[algorithm]["rsu_radius"].append(rsu_radius)

        data_by_num_rsus[(algorithm, rsu_radius)]["num_rsus"].append(num_rsus)
        data_by_num_rsus[(algorithm, rsu_radius)]["coverage"].append(coverage)
        data_by_num_rsus[(algorithm, rsu_radius)]["avg_distance"].append(avg_distance)

        data_by_rsu_radius[(algorithm, num_rsus)]["rsu_radius"].append(rsu_radius)
        data_by_rsu_radius[(algorithm, num_rsus)]["coverage"].append(coverage)
        data_by_rsu_radius[(algorithm, num_rsus)]["avg_distance"].append(avg_distance)

    return data_by_algorithm, data_by_num_rsus, data_by_rsu_radius
