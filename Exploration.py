import pandas as pd
from matplotlib_venn import venn3, venn2

from Analyzer import Analyzer
from Utility import order_file1_and_file2, find_pairs_with_date_range, find_pairs, to_unique_file_tuples, order_package1_and_package2
from config import output_directory, input_directory, project_name
from matplotlib import pyplot as plt

from helper_scripts.join_helper import JoinHelper
from helper_scripts.pickle_helper import load_pickle, save_pickle
from helper_scripts.results_helper import add_result
from helper_scripts.smell_helper import get_project_class_smells_in_range, get_project_package_smells_in_range

analyzer = Analyzer()
join_helper = JoinHelper()
def run_exploration():
    calculate_smell_co_change_overlaps()


def calculate_smell_co_change_overlaps():
    dtw_pairs = set(overlap_dtw())
    mba_pairs = set(overlap_mba())
    fo_pairs = set(overlap_fo())
    #venn3([dtw_pairs, mba_pairs, fo_pairs], ('dtw', 'mba', 'fo'))
    #plt.show()


def print_overlap_of_algorithm(name, all_pairs_unsorted, co_changes_unsorted, include_class_level=True, include_package_level=True, calculate_chi_square=True):
    print("--- Overlap ", name, " co-changes and smells: ---")
    all_pairs_unsorted.dropna(inplace=True)
    co_changes_unsorted.dropna(inplace=True)
    all_pairs_df = order_package1_and_package2(order_file1_and_file2(all_pairs_unsorted))
    cc_pairs_df = order_package1_and_package2(order_file1_and_file2(co_changes_unsorted))

    class_smell_pairs_with_date = pd.DataFrame(columns=['file1', 'file2'])
    if include_class_level:
        class_smell_pairs_with_date = load_pickle("class_smell_pairs_with_date")
        if class_smell_pairs_with_date is None:
            class_smell_pairs_with_date = order_file1_and_file2(get_project_class_smells_in_range())  # df: file1, file2
            # Find file pairs that are part of the same class-level smell:
            class_smell_pairs_with_date = join_helper.perform_chunkified_pair_join(all_pairs_df, class_smell_pairs_with_date, level='file', compare_dates=False)
            save_pickle(class_smell_pairs_with_date, "class_smell_pairs_with_date")


    package_smell_pairs_with_date = pd.DataFrame(columns=['file1', 'file2'])
    if include_package_level:
        package_smell_pairs_with_date = load_pickle("package_smell_pairs_with_date")
        if package_smell_pairs_with_date is None:
            package_smell_pairs_with_date = order_package1_and_package2(get_project_package_smells_in_range())  # df: package1, package2
            # We want to find file pairs whose package are part of the same smell:
            package_smell_pairs_with_date = join_helper.perform_chunkified_pair_join(all_pairs_df, package_smell_pairs_with_date, level='package', compare_dates=False)
            # Note: we are interested in (file1, file2) in package_smell_pairs

            save_pickle(package_smell_pairs_with_date, "package_smell_pairs_with_date")

    # Combine the pairs
    smell_pairs_with_date = pd.DataFrame()
    smell_pairs_with_date = smell_pairs_with_date.append(class_smell_pairs_with_date, sort=False)
    smell_pairs_with_date = smell_pairs_with_date.append(package_smell_pairs_with_date, sort=False)
    distinct_smelly_pairs = to_unique_file_tuples(smell_pairs_with_date)  # (file1, file2)

    all_file_pair_tuples = set(all_pairs_df.apply(lambda row: (row.file1, row.file2), axis=1))

    relevant_smelly_pairs = set(distinct_smelly_pairs).intersection(all_file_pair_tuples)

    overlapping_pairs = to_unique_file_tuples(join_helper.perform_chunkified_pair_join(cc_pairs_df, smell_pairs_with_date))

    print(name, " all pairs:\t\t", len(all_pairs_df))
    print(name, " co-change pairs:\t\t", len(cc_pairs_df))
    print("All smell pairs:\t\t", len(distinct_smelly_pairs))
    print("Relevant smell pairs:\t\t", len(relevant_smelly_pairs))
    print("Overlapping pairs:\t\t", len(overlapping_pairs))
    print("Overlap ratio:\t\t", 0 if len(relevant_smelly_pairs) == 0 else 100 * (len(overlapping_pairs) / len(relevant_smelly_pairs)))
    print("overlapping pairs:")
    #for pair in overlapping_pairs:
    #    print(pair[0], ", ", pair[1])
    # save results
    add_result(project_name, name+"_all_pairs", len(all_pairs_df))
    add_result(project_name, name + "_cc_pairs", len(cc_pairs_df))
    add_result(project_name, name + "_distinct_smelly_pairs", len(distinct_smelly_pairs))
    add_result(project_name, name + "_relevant_smelly_pairs", len(relevant_smelly_pairs))
    add_result(project_name, name + "_overlapping_pairs", len(overlapping_pairs))

    if calculate_chi_square:
        cc_tuples = to_unique_file_tuples(cc_pairs_df)
        analyzer.analyze_results(overlapping_pairs, distinct_smelly_pairs, cc_tuples, all_file_pair_tuples)

    return overlapping_pairs


def overlap_dtw():
    return print_overlap_of_algorithm("DTW",
                                      find_pairs(output_directory + "/file_pairs_dtw.csv"),
                                      find_pairs_with_date_range(output_directory + "/dtw.csv", '%Y-%m-%d %H:%M:%S'),
                                      True,
                                      True,
                                      True)


def overlap_mba():
    return print_overlap_of_algorithm("MBA",
                                      find_pairs(output_directory + "/file_pairs_mba.csv"),
                                      find_pairs_with_date_range(output_directory + "/mba.csv", '%Y-%m-%d %H:%M:%S'),
                                      True,
                                      True,
                                      True)


def overlap_fo():
    return print_overlap_of_algorithm("FO",
                                      find_pairs(input_directory + "/file_pairs.csv"),
                                      find_pairs_with_date_range(input_directory + "/cochanges.csv", '%d-%m-%Y'),
                                      True,
                                      True,
                                      True)

