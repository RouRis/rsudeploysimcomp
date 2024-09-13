from rsudeploysimcomp.AllJunctions.all_junctions import AllJunctions
from rsudeploysimcomp.BranchAndBound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.DensityBased.densitybased import DensityBased
from rsudeploysimcomp.GARSUD.garsud import GARSUD
from rsudeploysimcomp.Plotter.plotter import Plotter, plot, plot_exec_time_algorithm, plot_exec_time_pipeline
from rsudeploysimcomp.PMCP_B.pmcp_b import PMCB_P
from rsudeploysimcomp.SUMOInterface.sumoparser import SUMOParser
from rsudeploysimcomp.Utils.utils import get_hyperparameter, load_config, update_config

# TODO: Schleife - über RSU-radius - über Num_RSUS (+2)
# TODO: Plot Coverage over NUM RSU
# TODO: Plot Avg Distance over NUM RSU
# TODO: Plot Avg Distance Histogram per time-step
# TODO: Plot Avg Distance Histogram (interval 50m)
# TODO: Plot Coverage Histogram per time-step / or over all time
# TODO: ExecTime of Pipeline


def main():
    config = load_config()

    num_rsus = config["General"]["num_rsus"]
    rsu_radius = config["General"]["rsu_radius"]
    grid_size = config["General"]["grid_size"]

    run_garsud = bool(config["Algorithms"]["GARSUD"]["run"])
    run_pmcp_b = bool(config["Algorithms"]["PMCP_B"]["run"])
    run_all_junctions = bool(config["Algorithms"]["AllJunctions"]["run"])
    run_density_based = bool(config["Algorithms"]["DensityBased"]["run"])
    run_branch_and_bound = bool(config["Algorithms"]["BranchAndBound"]["run"])

    # Quick info message to show which algorithms will run
    print("Running simulations with the following algorithms:")
    if run_garsud:
        print("  - GARSUD")
    if run_pmcp_b:
        print("  - PMCP_B")
    if run_all_junctions:
        print("  - AllJunctions")
    if run_density_based:
        print("  - DensityBased")
    if run_branch_and_bound:
        print("  - BranchAndBound")

    print("-" * 40)

    # Path to Plot-Directory:
    plot_directory_path = (
        config["General"]["base_path"]
        + config["General"]["rsudeploysimcomp_path"]
        + config["General"]["plot_map_path"]
    )

    print("Configuration: num_rsus={} | grid_size={} | rsu_radius={}\n".format(num_rsus, grid_size, rsu_radius))

    sumoparser = SUMOParser()
    sumoparser.check_grid_size_radius_relation()

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
    print("-" * 40)


if __name__ == "__main__":
    conf = load_config()

    num_rsus_list = get_hyperparameter(conf, "num_rsus")
    rsu_radius_list = get_hyperparameter(conf, "rsu_radius")
    grid_size_list = get_hyperparameter(conf, "grid_size")

    # Quick info message to show the picked hyperparameters
    print("Running simulations with the following hyperparameters:")
    print(f"  Grid Size: {grid_size_list}")
    print(f"  RSU Radius: {rsu_radius_list}")
    print(f"  Number of RSUs: {num_rsus_list}")
    print("-" * 40)

    for grid_size_counter in grid_size_list:
        for rsu_radius_counter in rsu_radius_list:
            for num_rsus_counter in num_rsus_list:
                update_config(num_rsus_counter, rsu_radius_counter, grid_size_counter)
                main()
                pass

    update_config(num_rsus_list, rsu_radius_list, grid_size_list)

    plot(num_rsus_list, rsu_radius_list)

    plot_exec_time_pipeline(
        in_file="ExecTime/Pipeline/pipeline_exec_time.csv",
        out_file="Plots/ExecTime/pipeline_exec_time.png",
    )
    plot_exec_time_algorithm(
        in_file="ExecTime/Algorithms/algorithms_exec_time.csv",
        out_file="Plots/ExecTime/algorithms_exec_time.png",
    )
