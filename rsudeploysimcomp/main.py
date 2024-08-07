import os

from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions
from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import RSU_SIM_Interface
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.utils import load_config
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased


def main():
    config = load_config("test")
    # config = load_config("sim")

    grid_size = int(config["sumo_interface"]["xml_parser"]["grid_size"])  # Set grid size here
    num_rsus = config["pmcp_b"]["num_rsus"]  # Set maximum number of RSUs here
    rsu_radius = config["general"]["rsu_radius"]
    parser = SUMOParser(grid_size=grid_size)
    # PMCP-B
    pmcp = PMCB_P(parser, num_rsus)
    # All junctions
    all_junctions = AllJunctions(parser)
    # Density_based
    density_based = DensityBased(parser, num_rsus)
    # Garsud
    garsud = GARSUD(sumoparser=parser, num_generations=100, num_parents_mating=10, sol_per_pop=20, num_rsus=10)
    garsud.setup_ga()
    garsud.run()
    # Branch and Bound
    branch_and_bound = BranchAndBound(parser, num_rsus)
    print(branch_and_bound.optimal_value)
    print(branch_and_bound.optimal_solution)
    print(branch_and_bound.picked_junctions)

    rsu_sim_interface = RSU_SIM_Interface()

    rsu_sim_interface.export_picked_locations_to_csv("picked_locations_pmcp.csv", pmcp.picked_junctions)
    rsu_sim_interface.export_picked_locations_to_csv("picked_locations_all.csv", all_junctions.data)
    rsu_sim_interface.export_picked_locations_to_csv(
        "picked_locations_density.csv", density_based.picked_junctions
    )
    rsu_sim_interface.export_picked_locations_to_csv("picked_locations_garsud.csv", garsud.picked_junctions)
    rsu_sim_interface.convert_csv_to_parquet("picked_locations_garsud.csv", "picked_locations_garsud.parquet")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    tx_data_parquet_path = os.path.join(current_dir, "Koln_v1", "disolv", "tx_data.parquet")

    coverage, avg_distance = rsu_sim_interface.parse_output_file(tx_data_parquet_path, rsu_radius)

    print(coverage)
    print(avg_distance)

if __name__ == "__main__":
    main()
