from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions

# from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.plotter.plotter import Plotter, plot
from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.utils import load_config, update_config_num_rsus, convert_to_serializable
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
    print(
        "Configuration: num_rsus={} | grid_size={} | rsu_radius={}\n".format(
            num_rsus, grid_size, rsu_radius
        )
    )

    sumoparser = SUMOParser()

    all_junctions = AllJunctions(sumoparser=sumoparser)
    plotter = Plotter(all_junctions.picked_junctions)
    density_based = DensityBased(sumoparser=sumoparser)
    pmcp_b = PMCB_P(sumoparser=sumoparser)
    garsud = GARSUD(sumoparser=sumoparser)
    # branch_and_bound = BranchAndBound(sumoparser=sumoparser)

    # Path to Plot-Directory:
    plot_directory_path = (
            config["general"]["base_path"]
            + config["general"]["rsudeploysimcomp_path"]
            + config["general"]["plot_map_path"]
    )

    # All junctions
    all_junctions_plot_path = plot_directory_path + f"/AllJunctions_{num_rsus}_{rsu_radius}.png"
    plotter.run(algorithm_name="AllJunctions",
                rsu_positions=all_junctions.picked_junctions,
                coverage=all_junctions.coverage,
                avg_distance=all_junctions.avg_distance,
                save_path=all_junctions_plot_path,
                )
    print("\nAllJunctions/n")
    print("Coverage: " + str(all_junctions.coverage))
    print("Avg-Distance: " + str(all_junctions.avg_distance))

    # PMCP-B
    print("\nRunning PMCP-B...")
    pmcp_b.run()
    pmcp_plot_path = plot_directory_path + f"/PMCP_B{num_rsus}_{rsu_radius}.png"
    plotter.run(algorithm_name="PMCP_B",
                rsu_positions=pmcp_b.picked_junctions,
                coverage=pmcp_b.coverage,
                avg_distance=pmcp_b.avg_distance,
                save_path=pmcp_plot_path)
    print("Coverage: " + str(pmcp_b.coverage))
    print("Avg-Distance: " + str(pmcp_b.avg_distance))

    # Density_based
    print("\nRunning Density-Based...")
    density_based.run()
    density_based_plot_path = plot_directory_path + f"/DensityBased{num_rsus}_{rsu_radius}.png"
    plotter.run(algorithm_name="Density-Based",
                rsu_positions=density_based.picked_junctions,
                coverage=density_based.coverage,
                avg_distance=density_based.avg_distance,
                save_path=density_based_plot_path,
                )
    print("Coverage: " + str(density_based.coverage))
    print("Avg-Distance: " + str(density_based.avg_distance))

    # Garsud
    #print("\nRunning GARSUD...")
    #garsud.setup_ga()
    #garsud.run()
    #garsud_plot_path = plot_directory_path + f"/GARSUD_{num_rsus}_{rsu_radius}.png"
    #plotter.run(
    #    algorithm_name="GARSUD",
    #    rsu_positions=garsud.picked_junctions,
    #    coverage=garsud.coverage,
    #    avg_distance=garsud.avg_distance,
    #    save_path=garsud_plot_path,
    #)
    #print("Coverage: " + str(garsud.coverage))
    #print("Avg-Distance: " + str(garsud.avg_distance))

    # Branch and Bound
    # print("\nRunning Branch & Bound...")
    # branch_and_bound.run()
    # print(branch_and_bound.optimal_value)
    # print(branch_and_bound.optimal_solution)
    # print(branch_and_bound.picked_junctions)
    print("\nFinished")


if __name__ == "__main__":

    for num_rsus_counter in range(5, 8, 2):
        update_config_num_rsus(num_rsus_counter)
        # Run simulation
        main()
    plot()

