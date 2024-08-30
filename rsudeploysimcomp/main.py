from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions
from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.plotter.plotter import (
    Plotter,
    plot_avg_distance_histogram,
    plot_avg_distance_per_timestep,
    plot_coverage_histogram,
    plot_coverage_per_timestep,
)
from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.utils import load_config
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased

# TODO: Schleife - über RSU-radius - über Num_RSUS (+2)
# TODO: Plot Coverage over NUM RSU
# TODO: Plot Avg Distance over NUM RSU
# TODO: Plot Avg Distance Histogram per time-step
# TODO: Plot Avg Distance Histogram (interval 50m)
# TODO: Plot Coverage Histogram per time-step / or over all time
# TODO: Execution Time of Pipeline


def main():
    config = load_config()
    num_rsus = config["general"]["num_rsus"]
    grid_size = config["general"]["grid_size"]

    rsu_radius = config["general"]["rsu_radius"]
    run_garsud = bool(config["algorithms"]["GARSUD"]["run"])
    run_pmcp_b = bool(config["algorithms"]["PMCP_B"]["run"])
    run_all_junctions = bool(config["algorithms"]["AllJunctions"]["run"])
    run_density_based = bool(config["algorithms"]["DensityBased"]["run"])
    run_branch_and_bound = bool(config["algorithms"]["BranchAndBound"]["run"])

    # Path to Plot-Directory:
    plot_directory_path = (
        config["general"]["base_path"]
        + config["general"]["rsudeploysimcomp_path"]
        + config["general"]["plot_map_path"]
    )

    print("Configuration: num_rsus={} | grid_size={} | rsu_radius={}\n".format(num_rsus, grid_size, rsu_radius))

    sumoparser = SUMOParser()
    plotter = Plotter()

    if run_all_junctions:
        all_junctions = AllJunctions(sumoparser=sumoparser)
        plotter.all_junctions = all_junctions.picked_junctions
        all_junctions_plot_path = plot_directory_path + f"/AllJunctions_{num_rsus}_{rsu_radius}.png"
        plotter.run(
            algorithm_name="AllJunctions",
            rsu_positions=all_junctions.picked_junctions,
            coverage=all_junctions.coverage,
            avg_distance=all_junctions.avg_distance,
            save_path=all_junctions_plot_path,
        )
        print("\nAllJunctions/n")
        print("Coverage: " + str(all_junctions.coverage))
        print("Avg-Distance: " + str(all_junctions.avg_distance))

    if run_density_based:
        density_based = DensityBased(sumoparser=sumoparser)
        # Density_based
        print("\nRunning Density-Based...")
        density_based.run()
        density_based_plot_path = plot_directory_path + f"/DensityBased{num_rsus}_{rsu_radius}.png"
        plotter.run(
            algorithm_name="Density-Based",
            rsu_positions=density_based.picked_junctions,
            coverage=density_based.coverage,
            avg_distance=density_based.avg_distance,
            save_path=density_based_plot_path,
        )
        print("Coverage: " + str(density_based.coverage))
        print("Avg-Distance: " + str(density_based.avg_distance))

    if run_pmcp_b:
        pmcp_b = PMCB_P(sumoparser=sumoparser)
        # PMCP-B
        print("\nRunning PMCP-B...")
        pmcp_b.run()
        pmcp_plot_path = plot_directory_path + f"/PMCP_B{num_rsus}_{rsu_radius}.png"
        plotter.run(
            algorithm_name="PMCP_B",
            rsu_positions=pmcp_b.picked_junctions,
            coverage=pmcp_b.coverage,
            avg_distance=pmcp_b.avg_distance,
            save_path=pmcp_plot_path,
        )
        print("Coverage: " + str(pmcp_b.coverage))
        print("Avg-Distance: " + str(pmcp_b.avg_distance))

    if run_garsud:
        garsud = GARSUD(sumoparser=sumoparser)
        # Garsud
        print("\nRunning GARSUD...")
        garsud.setup_ga()
        garsud.run()
        garsud_plot_path = plot_directory_path + f"/GARSUD_{num_rsus}_{rsu_radius}.png"
        plotter.run(
            algorithm_name="GARSUD",
            rsu_positions=garsud.picked_junctions,
            coverage=garsud.coverage,
            avg_distance=garsud.avg_distance,
            save_path=garsud_plot_path,
        )
        print("Coverage: " + str(garsud.coverage))
        print("Avg-Distance: " + str(garsud.avg_distance))

    if run_branch_and_bound:
        branch_and_bound = BranchAndBound(sumoparser=sumoparser)
        print("\nRunning Branch & Bound...")
        branch_and_bound.run()

    print("\nFinished")


if __name__ == "__main__":
    rsu_radius_range = range(100, 1000, 100)
    num_rsus_range = range(1, 10, 2)
    # for rsu_radius_counter in rsu_radius_range:
    #    for num_rsus_counter in num_rsus_range:
    #        update_config(num_rsus_counter, rsu_radius_counter)
    #        main()
    # plot(num_rsus_range, rsu_radius_range)

    plot_coverage_per_timestep("./Results/PMCP_B_1_100.json")
    plot_avg_distance_per_timestep("./Results/PMCP_B_1_100.json")
    plot_coverage_histogram("./Results/PMCP_B_1_100.json")
    plot_avg_distance_histogram("./Results/PMCP_B_1_100.json")
