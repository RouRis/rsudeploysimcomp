from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RsuDeployment
from rsudeploysimcomp.utils.config_loader import load_config
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased

import os

config = load_config("test")
# config = load_config("sim")

grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])
max_rsus = config["pmcp_b"]["max_rsus"]
pmcp_b_parser = SUMOParser(grid_size)

pmcb_p = PMCB_P(pmcp_b_parser, max_rsus)
densitybased = DensityBased(pmcp_b_parser, max_rsus)
print(pmcb_p.picked_locations)
print(densitybased.picked_locations)

def main():
    grid_size = 10  # Set grid size here
    max_rsus = 5  # Set maximum number of RSUs here

    parser = SUMOParser(grid_size=grid_size)
    rsu_deployment = RsuDeployment(sumo_parser=parser, max_rsus=max_rsus)

    picked_locations = rsu_deployment.get_picked_locations()
    print("Picked locations for RSU deployment:", picked_locations)

    rsu_deployment.export_picked_locations_to_csv("picked_locations.csv")

    for junction in parser.junctions:
        print(f"Junction {junction['id']} at ({junction['x']}, {junction['y']}) of type {junction['type']}")

if __name__ == "__main__":
    main()