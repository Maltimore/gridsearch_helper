import os
import argparse

import collect_results
import plotting

if __name__ == '__main__':
    # PARAMETERS
    # Specify which columns to plot as strings in a list. List can be empty.
    RELEVANT_PARAMETERS = ['noise_level']  # list of strings (list can be empty)
    # what variable to use as performance measure
    TARGET_COLUMN = 'run_time_seconds'  # string
    # is the performance better when the target variable is lower or when it is higher?
    LOWER_IS_BETTER = False  # bool
    # split up the analysis into separate parts for unique values in this column
    SPLIT_ANALYSIS_COLUMN = None  # string or None
    # only for 1 relevant parameter (len(RELEVANT_PARAMETERS) == 1): the order in which
    # to present the swarm/bar plot variables
    # should be None if no order is specified
    # this can also be used to control *which* entries are presented at all by only including the
    # relevant onces in the list
    VAR_ORDER = None#['normal', 'model_based', 'rupture_avoidance', 'both']

    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Path to root of gridsearch results')
    args = parser.parse_args()
    args.path = os.path.expanduser(args.path)

    # collect results
    results_path = os.path.join(args.path, 'job_outputs')
    df = collect_results.collect_results(results_path)
    df.to_csv(os.path.join(args.path, 'results_df.csv'))

    # plotting
    plot_path = os.path.join(args.path, 'plots')
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    plotting.plot(df, plot_path, RELEVANT_PARAMETERS, TARGET_COLUMN,
                  LOWER_IS_BETTER, SPLIT_ANALYSIS_COLUMN, VAR_ORDER)
