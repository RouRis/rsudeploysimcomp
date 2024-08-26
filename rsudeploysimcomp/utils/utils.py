import os
from math import sqrt

import json
import numpy as np
import yaml
import glob


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "app_config" + ".yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def update_config_num_rsus(num_rsus):
    """
    Update the configuration file with a new number of RSUs.
    """
    config_path = './config/app_config.yaml'

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Update the number of RSUs
    config["general"]["num_rsus"] = num_rsus

    # Save the updated configuration
    with open(config_path, 'w') as file:
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
    with open(file_path, 'r') as file:
        data = json.load(file)

    algorithm = data.get('algorithm')
    num_rsus = data.get('num_rsus')
    coverage = data.get('coverage')
    avg_distance = data.get('avg_distance')
    rsu_radius = data.get('rsu_radius')

    return algorithm, num_rsus, rsu_radius, coverage, avg_distance

def collect_data(file_pattern):
    file_paths = glob.glob(file_pattern)
    data_by_algorithm = {}
    for path in file_paths:
        algorithm, num_rsus, rsu_radius, coverage, avg_distance = extract_data_from_result_json(path)

        if algorithm not in data_by_algorithm:
            data_by_algorithm[algorithm] = {'num_rsus': [], 'coverage': [], 'avg_distance': [], 'rsu_radius': []}


        data_by_algorithm[algorithm]['num_rsus'].append(num_rsus)
        data_by_algorithm[algorithm]['coverage'].append(coverage)
        data_by_algorithm[algorithm]['avg_distance'].append(avg_distance)
        data_by_algorithm[algorithm]['rsu_radius'].append(rsu_radius)

    return data_by_algorithm
