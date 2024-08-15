import os

from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions
from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.rsu_simulator_interface.rsu_interface import (
    export_picked_locations_to_csv,
    parse_output_file,
)
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.utils import load_config
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased


def main():
    config = load_config()

    grid_size = int(config["general"]["grid_size"])  # Set grid size here
    num_rsus = config["general"]["num_rsus"]  # Set maximum number of RSUs here
    rsu_radius = config["general"]["rsu_radius"]
    sumoparser = SUMOParser(grid_size=grid_size)
    # PMCP-B
    pmcp = PMCB_P(sumoparser, num_rsus)
    # All junctions
    all_junctions = AllJunctions(sumoparser)
    # Density_based
    density_based = DensityBased(sumoparser, num_rsus)
    # Garsud

    # plot_deployment(density_based.picked_junctions, 'Density Based')
    # plot_deployment(pmcp.picked_junctions, 'PMCP-B')

    garsud = GARSUD(sumoparser=sumoparser)
    garsud.setup_ga()
    garsud.run()

    # Branch and Bound
    branch_and_bound = BranchAndBound(sumoparser, num_rsus)
    print(branch_and_bound.optimal_value)
    print(branch_and_bound.optimal_solution)
    print(branch_and_bound.picked_junctions)

    export_picked_locations_to_csv("picked_locations_pmcp.csv", pmcp.picked_junctions)
    export_picked_locations_to_csv("picked_locations_all.csv", all_junctions.data)
    export_picked_locations_to_csv("picked_locations_density.csv", density_based.picked_junctions)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    tx_data_parquet_path = os.path.join(current_dir, "Koln_v1", "disolv", "tx_data.parquet")

    coverage, avg_distance = parse_output_file(tx_data_parquet_path, rsu_radius)

    print(coverage)
    print(avg_distance)


if __name__ == "__main__":
    main()
