import os
import argparse

import collect_results
import plotting

if __name__ == '__main__':
    ##############################################################################################
    ##############################################################################################
    # PARAMETERS
    ##############################################################################################
    # Collect results
    # default values are being used if the run didn't finish yet and skip_unfinished_runs is False
    DEFAULT_VALUES = {}
    DEFAULT_VALUES['first_success'] = 150
    RESULT_KEYS = ('first_success',)
    skip_unfinished_runs = True
    ##############################################################################################
    # Plotting
    # Specify which columns to plot as strings in a list. List can be empty.
    RELEVANT_PARAMETERS = ['name']  # list of strings (list can be empty)
    # what variable to use as performance measure
    TARGET_COLUMN = 'first_success'  # string
    # is the performance better when the target variable is lower or when it is higher?
    LOWER_IS_BETTER = True  # bool
    # split up the analysis into separate parts for unique values in this column
    SPLIT_ANALYSIS_COLUMN = None  # string or None
    # only for 1 relevant parameter (len(RELEVANT_PARAMETERS) == 1): the order in which
    # to present the swarm/bar plot variables
    # should be None if no order is specified
    # this can also be used to control *which* entries are presented at all by only including the
    # relevant onces in the list
    VAR_ORDER = ['normal', 'hallucinate', 'neg_temp', 'hallucinate_&_neg_temp']
    ##############################################################################################
    ##############################################################################################

    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='results directory')
    args = parser.parse_args()

    # collect results
    results_path = os.path.join(args.path, 'results')
    df = collect_results.collect_results(
        results_path, DEFAULT_VALUES, RESULT_KEYS, skip_unfinished_runs)
    df.to_csv(os.path.join(args.path, 'results_df.csv'))

    # plotting
    plot_path = os.path.join(args.path, 'plots')
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    plotting.plot(
        df, plot_path, RELEVANT_PARAMETERS, TARGET_COLUMN, LOWER_IS_BETTER,
        SPLIT_ANALYSIS_COLUMN, VAR_ORDER)
