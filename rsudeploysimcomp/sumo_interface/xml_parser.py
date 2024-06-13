import gzip
import xml.etree.ElementTree as ET

import numpy as np

from rsudeploysimcomp.utils.config_loader import load_config

config = load_config()
path_to_fcd_xml = config["sumo_interface"]["xml_parser"]["path_to_fcd_xml"]


def find_element_attribute_in_xml_gz(gz_file_path, tag_name, attribute_name):
    """
    Finds the specified attribute of the first occurrence of a given tag in an XML file.

    Args:
        gz_file_path (str): Path to the .gz compressed XML file.
        tag_name (str): The name of the XML tag to search for.
        attribute_name (str): The name of the attribute to retrieve.

    Returns:
        The value of the specified attribute, or None if the tag or attribute is not found.
    """
    try:
        with gzip.open(gz_file_path, "rb") as f_in:
            # Create an iterator to parse the XML incrementally
            context = ET.iterparse(f_in, events=("start", "end"))

            # Iterate through the parsed elements
            for event, elem in context:
                # Check if the current element matches the specified tag
                if event == "start" and elem.tag == tag_name:
                    # Extract the specified attribute
                    attribute_value = elem.get(attribute_name)

                    # Clear the element to free up memory
                    elem.clear()

                    return attribute_value

                # Clear the element to free up memory
                elem.clear()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return None


def parse_max_xy():
    path_to_net_xml_gx = config["sumo_interface"]["xml_parser"]["path_to_net_xml_zip"]
    conv_boundary = find_element_attribute_in_xml_gz(path_to_net_xml_gx, "location", "convBoundary")
    if conv_boundary is None:
        return -1, -1
    else:
        conv_boundary_values = [float(x) for x in conv_boundary.split(",")]
        x_max = conv_boundary_values[2]
        y_max = conv_boundary_values[3]
        return x_max, y_max


class PmcpBParser:
    def __init__(self):
        self.grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])  # Number of cells per dimension
        self.vehicle_count = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.x_max, self.y_max = parse_max_xy()
        self.x_min, self.y_min = 0, 0
        self.generate_matrix_m()

    def get_grid_cell(self, x, y):
        """
        Determines the grid cell indices based on x and y coordinates.

        Args:
            x (float): x-coordinate of the vehicle.
            y (float): y-coordinate of the vehicle.

        Returns:
            int, int: Indices of the grid cell for the given x, y coordinates.
        """
        x_step = (self.x_max - self.x_min) / self.grid_size
        y_step = (self.y_max - self.y_min) / self.grid_size
        x_index = min(int((x - self.x_min) / x_step), self.grid_size - 1)
        y_index = min(int((y - self.y_min) / y_step), self.grid_size - 1)

        x_index = max(0, min(x_index, self.grid_size - 1))
        y_index = max(0, min(y_index, self.grid_size - 1))

        return x_index, y_index

    def generate_matrix_m(self):
        """
        Generates a 2D matrix of vehicle counts within a grid based on an XML file.

        Returns:
            numpy.ndarray: 2D matrix representing vehicle counts in each grid cell.
        """
        try:
            # Parse the XML file
            tree = ET.parse(path_to_fcd_xml)
            root = tree.getroot()
            # Iterate over each timestep
            for timestep in root.findall("timestep"):
                # Iterate over each vehicle within the timestep
                for vehicle in timestep.findall("vehicle"):
                    x = float(vehicle.get("x"))
                    y = float(vehicle.get("y"))
                    x_index, y_index = self.get_grid_cell(x, y)
                    self.vehicle_count[y_index, x_index] += 1

        except Exception as e:
            print(f"An error occurred while processing the XML file: {e}")


pmcp_b_parser = PmcpBParser()
print("2")
print(pmcp_b_parser.vehicle_count)
