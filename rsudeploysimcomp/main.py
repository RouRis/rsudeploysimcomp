from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions

# from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.plotter.plotter import Plotter
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

    print(
        "Configuration: num_rsus={} | grid_size={} | rsu_radius={}".format(
            config["general"]["num_rsus"], config["general"]["grid_size"], config["general"]["rsu_radius"]
        )
    )

    print("Starting Code: \n")

    print("SUMOParser Initialization...\n")
    sumoparser = SUMOParser()

    print("AllJunctions Initialization...\n")
    all_junctions = AllJunctions(sumoparser=sumoparser)

    print("plotter Initialization...\n")
    plotter = Plotter(all_junctions.picked_junctions)

    print("DensityBased Initialization...\n")
    density_based = DensityBased(sumoparser=sumoparser)

    print("PMCB_P Initialization...\n")
    pmcp = PMCB_P(sumoparser=sumoparser)

    print("GARSUD Initialization...\n")
    garsud = GARSUD(sumoparser=sumoparser, plotter=plotter)

    # print("BranchAndBound Initialization...\n")
    # branch_and_bound = BranchAndBound(sumoparser=sumoparser)

    # Path to Plot-Directory:
    plot_directory_path = (
        config["general"]["base_path"]
        + config["general"]["rsudeploysimcomp_path"]
        + config["general"]["plot_path"]
    )

    # All junctions
    all_junctions_plot_path = plot_directory_path + "/AllJunctions.png"
    plotter.plot_deployment_map(
        rsu_positions=all_junctions.picked_junctions,
        title="AllJunctions",
        coverage=all_junctions.coverage,
        avg_distance=all_junctions.avg_distance,
        save_path=all_junctions_plot_path,
    )
    print("\nAllJunctions/n")
    print("Coverage: " + str(all_junctions.coverage))
    print("Avg-Distance: " + str(all_junctions.avg_distance))

    # PMCP-B
    print("\nRunning PMCP-B...")
    pmcp.run()
    pmcp_plot_path = plot_directory_path + "/PMCP_B.png"
    plotter.plot_deployment_map(
        rsu_positions=pmcp.picked_junctions,
        title="PMCP-B",
        coverage=pmcp.coverage,
        avg_distance=pmcp.avg_distance,
        save_path=pmcp_plot_path,
    )
    plotter.plot_histo_avg_distance_per_timestep()
    plotter.plot_histo_coverage_per_timestep()
    print("Coverage: " + str(pmcp.coverage))
    print("Avg-Distance: " + str(pmcp.avg_distance))

    # Density_based
    print("\nRunning Density-Based...")
    density_based.run()
    density_based_plot_path = plot_directory_path + "/DensityBased.png"
    plotter.plot_deployment_map(
        rsu_positions=density_based.picked_junctions,
        title="DensityBased",
        coverage=density_based.coverage,
        avg_distance=density_based.avg_distance,
        save_path=density_based_plot_path,
    )
    print("Coverage: " + str(density_based.coverage))
    print("Avg-Distance: " + str(density_based.avg_distance))

    # Garsud
    print("\nRunning GARSUD...")
    garsud.setup_ga()
    garsud.run()
    garsud_plot_path = plot_directory_path + "/GARSUD.png"
    plotter.plot_deployment_map(
        rsu_positions=garsud.picked_junctions,
        title="GARSUD",
        coverage=garsud.coverage,
        avg_distance=garsud.avg_distance,
        save_path=garsud_plot_path,
    )
    print("Coverage: " + str(garsud.coverage))
    print("Avg-Distance: " + str(garsud.avg_distance))

    # Branch and Bound
    # print("\nRunning Branch & Bound...")
    # branch_and_bound.run()
    # print(branch_and_bound.optimal_value)
    # print(branch_and_bound.optimal_solution)
    # print(branch_and_bound.picked_junctions)

    print("\nFinished")


if __name__ == "__main__":
    main()
