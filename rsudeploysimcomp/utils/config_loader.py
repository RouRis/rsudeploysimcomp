import os

import yaml


def load_config(env):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "app_config_" + env + ".yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config
