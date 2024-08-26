from rsudeploysimcomp.all_junctions.all_junctions import AllJunctions

# from rsudeploysimcomp.branch_and_bound.branch_and_bound import BranchAndBound
from rsudeploysimcomp.garsud.garsud import GARSUD
from rsudeploysimcomp.plotter.plotter import Plotter, plot_metrics_for_all_algorithms_over_num_rsus
from rsudeploysimcomp.pmcp_b.pmcp_b import PMCB_P
from rsudeploysimcomp.sumo_interface.sumo_parser import SUMOParser
from rsudeploysimcomp.utils.utils import load_config, update_config_num_rsus, convert_to_serializable
from rsudeploysimcomp.vehicle_density_based.densitybased import DensityBased

import os
import json
import numpy as np


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
        "Configuration: num_rsus={} | grid_size={} | rsu_radius={}\n".format(
            config["general"]["num_rsus"], config["general"]["grid_size"], config["general"]["rsu_radius"]
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
    all_junctions_plot_path = plot_directory_path + "/AllJunctions.png"
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
    pmcp_plot_path = plot_directory_path + "/PMCP_B.png"
    plotter.run(algorithm_name="PMCP-B",
                rsu_positions=pmcp_b.picked_junctions,
                coverage=pmcp_b.coverage,
                avg_distance=pmcp_b.avg_distance,
                save_path=pmcp_plot_path)
    print("Coverage: " + str(pmcp_b.coverage))
    print("Avg-Distance: " + str(pmcp_b.avg_distance))

    # Density_based
    print("\nRunning Density-Based...")
    density_based.run()
    density_based_plot_path = plot_directory_path + "/DensityBased.png"
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
    #garsud_plot_path = plot_directory_path + "/GARSUD.png"
    #plotter.run(
    #    algorithm_name="GARSUD",
    #    rsu_positions=garsud.picked_junctions,
    #    coverage=garsud.coverage,
    #    avg_distance=garsud.avg_distance,
    #    save_path=garsud_plot_path,
    #)
    #print("Coverage: " + str(garsud.coverage))
    #print("Avg-Distance: " + str(garsud.avg_distance))

    results = {
        "AllJunctions": {"coverage": None, "avg_distance": None},
        "PMCP-B": {"coverage": None, "avg_distance": None},
        "DensityBased": {"coverage": None, "avg_distance": None},
        #    "GARSUD": {"coverage": None, "avg_distance": None}
    }

    # All junctions result
    results["AllJunctions"]["coverage"] = all_junctions.coverage
    results["AllJunctions"]["avg_distance"] = all_junctions.avg_distance

    # PMCP-B result
    results["PMCP-B"]["coverage"] = pmcp_b.coverage
    results["PMCP-B"]["avg_distance"] = pmcp_b.avg_distance

    # DensityBased result
    results["DensityBased"]["coverage"] = density_based.coverage
    results["DensityBased"]["avg_distance"] = density_based.avg_distance

    # GARSUD result
    #results["GARSUD"]["coverage"] = garsud.coverage
    #results["GARSUD"]["avg_distance"] = garsud.avg_distance

    # Branch and Bound
    # print("\nRunning Branch & Bound...")
    # branch_and_bound.run()
    # print(branch_and_bound.optimal_value)
    # print(branch_and_bound.optimal_solution)
    # print(branch_and_bound.picked_junctions)
    print("\nFinished")

    return results


if __name__ == "__main__":
    results_dir = "results"  # Directory to save results
    os.makedirs(results_dir, exist_ok=True)

    all_results = []  # To store results from all runs for combined analysis
    for num_rsus in range(5, 8, 2):
        print(f"\nRunning simulation with {num_rsus} RSUs...\n")
        update_config_num_rsus(num_rsus)

        # Run simulation
        results = main()
        all_results.append({"rsu_count": num_rsus, "results": results})

        # Save individual run results
        rsu_result_dir = os.path.join(results_dir, f"rsu_{num_rsus}")
        os.makedirs(rsu_result_dir, exist_ok=True)

        for algorithm, data in results.items():
            algo_result_dir = os.path.join(rsu_result_dir, algorithm)
            os.makedirs(algo_result_dir, exist_ok=True)
            result_file_path = os.path.join(algo_result_dir, "results.json")

            # Convert data to a JSON serializable format
            serializable_data = convert_to_serializable(data)

            with open(result_file_path, 'w') as f:
                json.dump(serializable_data, f, indent=4)

        # Save all results to a single file for later analysis
    combined_results_file = os.path.join(results_dir, "combined_results.json")
    serializable_all_results = convert_to_serializable(all_results)
    with open(combined_results_file, 'w') as f:
        json.dump(serializable_all_results, f, indent=4)

    print("\nAll simulations completed. Results saved to the results directory.")

    # Load the combined results
    combined_results_file = "results/combined_results.json"
    with open(combined_results_file, 'r') as f:
        all_results = json.load(f)

    # Prepare data for plotting
    rsu_counts = [result["rsu_count"] for result in all_results]

    # Create dictionaries to store data by algorithm
    coverage_data = {algo: [] for algo in all_results[0]["results"].keys()}
    avg_distance_data = {algo: [] for algo in all_results[0]["results"].keys()}

    # Populate the dictionaries with data
    for result in all_results:
        for algo in result["results"]:
            coverage_data[algo].append(result["results"][algo]["coverage"])
            avg_distance_data[algo].append(result["results"][algo]["avg_distance"])

    plot_metrics_for_all_algorithms_over_num_rsus(coverage_data, avg_distance_data, rsu_counts)
