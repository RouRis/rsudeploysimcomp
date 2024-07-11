from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.config_loader import load_config
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased


def main():
    config = load_config("test")
    # config = load_config("sim")

    grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])  # Set grid size here
    max_rsus = config["pmcp_b"]["max_rsus"]  # Set maximum number of RSUs here

    parser = SUMOParser(grid_size=grid_size)
    pmcp = PMCB_P(parser, max_rsus)
    density_based = DensityBased(parser, max_rsus)
    rsu_deployment = RSU_SIM_Interface()

    rsu_deployment.export_picked_locations_to_csv("picked_locations_pmcp.csv", pmcp.picked_junctions)
    rsu_deployment.export_picked_locations_to_csv("picked_locations_all.csv", parser.junctions)
    rsu_deployment.export_picked_locations_to_csv("picked_locations_density.csv", density_based.picked_junctions)

    # for junction in parser.junctions:
    # print(f"Junction {junction['id']} at ({junction['x']}, {junction['y']}) of type {junction['type']}")


if __name__ == "__main__":
    main()
