import math
import xml.etree.ElementTree as ET

import numpy as np
from scipy.sparse import lil_matrix

from rsudeploysimcomp.Utils.utils import load_config

config = load_config()

path_to_fcd_xml = (
    config["General"]["base_path"]
    + config["VanetInterface"]["raw_path"]
    + config["VanetInterface"]["scenario"]
    + "/koln_fcd.xml"
)

path_to_net_xml_gx = (
    config["General"]["base_path"]
    + config["VanetInterface"]["raw_path"]
    + config["VanetInterface"]["scenario"]
    + "/koln.net.xml"
)


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
        # Create an iterator to parse the XML incrementally
        context = ET.iterparse(gz_file_path, events=("start", "end"))

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
    conv_boundary = find_element_attribute_in_xml_gz(path_to_net_xml_gx, "location", "convBoundary")
    if conv_boundary is None:
        return -1, -1
    else:
        conv_boundary_values = [float(x) for x in conv_boundary.split(",")]
        x_max = conv_boundary_values[2]
        y_max = conv_boundary_values[3]
        return x_max, y_max


def parse_net_offset():
    net_offset = find_element_attribute_in_xml_gz(path_to_net_xml_gx, "location", "netOffset")
    if net_offset is None:
        return -1, -1
    else:
        net_offset_values = [float(x) for x in net_offset.split(",")]
        x_offset = net_offset_values[0]
        y_offset = net_offset_values[1]
        return x_offset, y_offset


class SUMOParser:
    def __init__(self):
        print("SUMOParser Initialization...\n")
        self.config = load_config()
        self.rsu_radius = self.config["General"]["rsu_radius"]
        self.grid_size = self.config["General"]["grid_size"]
        self.M = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.P = lil_matrix(
            (self.grid_size * self.grid_size, self.grid_size * self.grid_size), dtype=float
        )  # Sparse migration matrix
        self.x_max, self.y_max = parse_max_xy()
        self.x_offset, self.y_offset = parse_net_offset()
        self.x_min, self.y_min = 0, 0
        self.x_step, self.y_step = 0, 0
        self.vehicle_paths = {}
        self.location_vehicles = {}
        self.junctions = []
        self.parse_junctions()
        self.generate_matrix_m_and_p()

    def check_grid_size_radius_relation(self):
        radius1 = math.sqrt(2 * self.x_step * self.x_step)
        radius2 = math.sqrt(2 * self.y_step * self.y_step)

        cuboid_length = math.sqrt(self.rsu_radius * self.rsu_radius * 0.5)

        grid_size_1 = (self.x_max - self.x_min) / cuboid_length
        grid_size_2 = (self.y_max - self.y_min) / cuboid_length

        print(f"Recommended grid_size for given radius: between {grid_size_1} and {grid_size_2}")
        print(f"Recommended radius for given grid_size: between {radius1} and {radius2}")

    def get_grid_cell(self, x, y):
        """
        Determines the grid cell indices based on x and y coordinates.

        Args:
            x (float): x-coordinate of the vehicle.
            y (float): y-coordinate of the vehicle.

        Returns:
            int, int: Indices of the grid cell for the given x, y coordinates.
        """
        self.x_step = (self.x_max - self.x_min) / self.grid_size
        self.y_step = (self.y_max - self.y_min) / self.grid_size
        x_index = min(int((x - self.x_min) / self.x_step), self.grid_size - 1)
        y_index = min(int((y - self.y_min) / self.y_step), self.grid_size - 1)
        x_index = max(0, min(x_index, self.grid_size - 1))
        y_index = max(0, min(y_index, self.grid_size - 1))

        return x_index, y_index

    def parse_junctions(self):
        try:
            tree = ET.parse(path_to_net_xml_gx)
            root = tree.getroot()
            for junction in root.findall("junction"):
                self.junctions.append(
                    {
                        "id": junction.get("id"),
                        "x": float(junction.get("x")),
                        "y": float(junction.get("y")),
                        "type": junction.get("type"),
                    }
                )
            self.junctions.sort(key=lambda j: (j["x"], j["y"]))
        except Exception as e:
            print(f"An error occurred while parsing junctions: {e}")

    def generate_matrix_m_and_p(self):
        """
        Generates a 2D matrix of vehicle counts within a grid (matrix M)
        and a matrix of migration ratios between adjacent grid cells (matrix P).

        Returns:
            numpy.ndarray: 2D matrix M, representing vehicle counts in each grid cell.
            numpy.ndarray: 2D matrix P, representing migration ratios between adjacent grid cells.
        """
        vehicle_locations = {}
        vehicle_ids = [[set() for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        try:
            # Parse the XML file
            tree = ET.parse(path_to_fcd_xml)
            root = tree.getroot()
            # Iterate over each timestep
            for timestep in root.findall("timestep"):
                # Iterate over each vehicle within the timestep
                for vehicle in timestep.findall("vehicle"):
                    vehicle_id = vehicle.get("id")
                    x = float(vehicle.get("x"))
                    y = float(vehicle.get("y"))
                    current_cell = self.get_grid_cell(x, y)
                    vehicle_ids[current_cell[0]][current_cell[1]].add(vehicle_id)

                    # Update vehicle_paths dictionary
                    if vehicle_id not in self.vehicle_paths:
                        self.vehicle_paths[vehicle_id] = set()
                    self.vehicle_paths[vehicle_id].add(current_cell)

                    # Update location_vehicles dictionary
                    cell_key = (current_cell[0], current_cell[1])
                    if cell_key not in self.location_vehicles:
                        self.location_vehicles[cell_key] = set()
                    self.location_vehicles[cell_key].add(vehicle_id)

                    # Update the vehicle's current location
                    if vehicle_id not in vehicle_locations:
                        vehicle_locations[vehicle_id] = {"previous": None, "current": current_cell}
                    else:
                        vehicle_locations[vehicle_id]["previous"] = vehicle_locations[vehicle_id]["current"]
                        vehicle_locations[vehicle_id]["current"] = current_cell

                    previous_cell = vehicle_locations[vehicle_id]["previous"]

                    if previous_cell is not None and previous_cell != current_cell:
                        from_index = previous_cell[0] * self.grid_size + previous_cell[1]
                        to_index = current_cell[0] * self.grid_size + current_cell[1]
                        self.P[from_index, to_index] += 1
            # Count the number of unique vehicles for each grid cell
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    self.M[i, j] = len(vehicle_ids[i][j])
            # Normalize matrix P to get migration ratios
            for i in range(self.P.shape[0]):
                row_sum = np.sum(self.P[i])
                if row_sum > 0:
                    self.P[i] /= row_sum

        except Exception as e:
            print(f"An error occurred while processing the XML file: {e}")
        self.P = self.P.tocsr()

    def generate_matrix_m_with_vehicle_paths(self):
        self.M = np.zeros((self.grid_size, self.grid_size), dtype=int)  # Reset the matrix
        for vehicle_id, path in self.vehicle_paths.items():
            for cell in path:
                self.M[cell[0], cell[1]] += 1
        return self.M
