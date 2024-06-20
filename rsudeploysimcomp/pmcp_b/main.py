from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.xml_parser import PmcpBParser
from rsudeploysimcomp.utils.config_loader import load_config

config = load_config("test")
# config = load_config("sim")

grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])
max_rsus = config["pmcp_b"]["max_rsus"]
pmcp_b_parser = PmcpBParser(grid_size)


loc = pmcp_b_parser.location_vehicles.get((3, 4))
for vehicle in loc:
    pmcp_b_parser.vehicle_paths.pop(vehicle)

pmcb_p = PMCB_P(pmcp_b_parser, max_rsus)
print(pmcb_p.picked_locations)
