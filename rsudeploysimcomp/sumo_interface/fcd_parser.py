import xml.etree.ElementTree as ET
import numpy as np
import yaml
from rsudeploysimcomp.utils.config_loader import load_config

config = load_config()

# Define the grid size (9x9)
grid_size = int(config['sumo_interface']['fcd_parser']['grid_size'])

# Initialize the 2D numpy matrix to count vehicles in each grid cell
vehicle_count = np.zeros((grid_size, grid_size), dtype=int)

# Define the bounds of the grid (assuming the area covered by the coordinates in the XML)
# These should be adjusted based on the actual coordinates range in your XML
x_min, x_max = 0, 6000
y_min, y_max = 0, 6000

# Function to determine the grid cell for given coordinates
def get_grid_cell(x, y, x_min, x_max, y_min, y_max, grid_size):
    x_step = (x_max - x_min) / grid_size
    y_step = (y_max - y_min) / grid_size
    x_index = min(int((x - x_min) / x_step), grid_size - 1)
    y_index = min(int((y - y_min) / y_step), grid_size - 1)
    return x_index, y_index

# Parse the XML file
tree = ET.parse('path_to_your_file.xml')
root = tree.getroot()

# Iterate over each timestep
for timestep in root.findall('timestep'):
    # Iterate over each vehicle within the timestep
    for vehicle in timestep.findall('vehicle'):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        x_index, y_index = get_grid_cell(x, y, x_min, x_max, y_min, y_max, grid_size)
        vehicle_count[y_index, x_index] += 1

# Print the resulting 2D numpy matrix
print(vehicle_count)