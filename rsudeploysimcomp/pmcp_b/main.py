from rsudeploysimcomp.utils.config_loader import load_config
from rsudeploysimcomp.sumo_interface.xml_parser import PmcpBParser
from rsudeploysimcomp.pmcp_b.pmcb_p import PMCB_P

config = load_config("test")
#config = load_config("sim")

grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])
max_rsus = config["pmcp_b"]["max_rsus"]
pmcp_b_parser = PmcpBParser(grid_size)

print(pmcp_b_parser.M)
print(pmcp_b_parser.P)
print(pmcp_b_parser.location_vehicles)
print(pmcp_b_parser.vehicle_paths)
#pmcb_p = PMCB_P(pmcp_b_parser.M, pmcp_b_parser.P, grid_size, max_rsus)
#print(pmcb_p.picked_locations)