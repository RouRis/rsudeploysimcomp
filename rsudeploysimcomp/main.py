from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.xml_parser import SUMOParser
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
