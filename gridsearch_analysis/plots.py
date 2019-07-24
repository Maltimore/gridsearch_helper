import pandas as pd
import os
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import argparse
import seaborn as sns


def parallel_coordinates(df, target_column, lower_is_better=True, **kwds):
    minimum_target = df[target_column].min()
    maximum_target = df[target_column].max()

    # process target column for plotting
    target_colors = df[target_column]
    target_colors = np.true_divide(target_colors - target_colors.min(), np.ptp(target_colors))
    if lower_is_better:
        target_colors = (target_colors - 1) * (-1)
    # sort df such that during plotting the better ones are drawn over the others
    df = df.sort_values(target_column, ascending=not lower_is_better)
    df = df.drop(columns=target_column)

    cols = df.columns

    x_ticks = list(range(len(cols)))

    # Create (X-1) sublots along x axis
    fig, axes = plt.subplots(1, len(x_ticks) - 1, sharey=False, figsize=(15, 5))
    # handle case X-1 == 1, in which case axes is not a list
    if len(x_ticks) - 1 == 1:
        axes = [axes]

    # Get min, max and range for each column
    # Normalize the data for each column
    tick_dict = {}
    for col in cols:
        tick_dict[col] = {}
        if type(df[col][0]) is str:  # treat variables of type string as categorical
            df[col] = df[col].astype('category')
            codes = df[col].cat.codes.copy()
            codes = np.true_divide(codes - codes.min(), np.ptp(codes))
            # Save the ticks and ticklabels
            # I assume that unique() returns the values in the order that they appear in the Series
            tick_dict[col]['ticks'] = codes.unique()
            tick_dict[col]['tick_labels'] = df[col].unique()
            # replace the categories with the computed codes
            df[col] = codes
        else:  # not categorical
            tick_dict[col]['tick_labels'] = df[col].unique()
            df[col] = np.true_divide(df[col] - df[col].min(), np.ptp(df[col]))
            tick_dict[col]['ticks'] = df[col].unique()
        df[col] = df[col] + np.random.normal(size=len(df), scale=0.02)

    # Loop over horizontally stacked subplots
    for i, ax in enumerate(axes):
        # loop over lines
        for idx in df.index:
            y = target_colors[idx]
            transparency = max(0.2, y**2)
            im = ax.plot(
                x_ticks, df.loc[idx, cols], color=cm.viridis(y), linewidth=3)#, alpha=transparency)
        ax.set_xlim([x_ticks[i], x_ticks[i + 1]])

    norm = mpl.colors.Normalize(vmin=minimum_target, vmax=maximum_target)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.viridis_r if lower_is_better else mpl.cm.viridis)
    cmap.set_array([])
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(cmap, cax=cbar_ax)

    # Set the tick positions and labels on y axis for each plot
    # Tick positions based on normalised data
    # Tick labels are based on original data
    for idx, ax in enumerate(axes):
        ax.yaxis.set_ticks(tick_dict[cols[idx]]['ticks'])
        ax.set_yticklabels(tick_dict[cols[idx]]['tick_labels'])
        ax.xaxis.set_major_locator(ticker.FixedLocator([idx]))
        ax.set_xticklabels([cols[idx]])

    # Move the final axis' ticks to the right-hand side
    ax = plt.twinx(axes[-1])
    idx = len(axes)
    ax.yaxis.set_ticks(tick_dict[cols[idx]]['ticks'])
    ax.set_yticklabels(tick_dict[cols[idx]]['tick_labels'])
    ax.xaxis.set_major_locator(ticker.FixedLocator([x_ticks[-2], x_ticks[-1]]))
    ax.set_xticklabels([cols[-2], cols[-1]])
    # Remove space between subplots
    plt.subplots_adjust(wspace=0)


if __name__ == '__main__':
    ################################################################################################
    # PARAMETERS
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
    ################################################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='results directory')
    path = parser.parse_args().path

    plot_path = os.path.join(path, 'plots')
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    df = pd.read_csv(os.path.join(path, 'results_df.csv'))

    # get the y_max as the maximum of the target column + 3% (for aesthetic)
    y_max = df[TARGET_COLUMN].max()
    y_max += 0.03 * y_max

    # check whether we have to split the analysis into different groups
    # if not, create a fake group called "all"
    if SPLIT_ANALYSIS_COLUMN is None:
        groups = {'all': df}.items()
    else:
        groups = df.groupby(SPLIT_ANALYSIS_COLUMN)

    # iterate over the groups for our split analysis
    for groupname, df in groups:
        print('Processing group {} = {}'.format(SPLIT_ANALYSIS_COLUMN if not None else "group", groupname))

        if len(RELEVANT_PARAMETERS) == 0:
            # swarm plot
            plot = sns.swarmplot(y=TARGET_COLUMN, data=df)
            fig = plot.get_figure()
            plot.set_xticklabels(plot.get_xticklabels(), rotation=90)
            plot.set_ylim([0, y_max])
            plot.grid(axis='y')
            fig.savefig(os.path.join(plot_path, '{}={}_swarmplot.png'.format(SPLIT_ANALYSIS_COLUMN, groupname)))
            plt.clf()

            # bar plot
            plt.bar(0, df[TARGET_COLUMN].describe().loc['mean'], yerr=df[TARGET_COLUMN].describe().loc['std'])
            plt.xlim([-1, 1])
            plt.ylim([0, y_max])
            plt.savefig(os.path.join(plot_path, '{}={}_barplot.png'.format(SPLIT_ANALYSIS_COLUMN, groupname)))
            plt.clf()

        elif len(RELEVANT_PARAMETERS) == 1:
            relevant_col = RELEVANT_PARAMETERS[0]

            # swarm plot
            plot = sns.swarmplot(x=relevant_col, y=TARGET_COLUMN, data=df, order=VAR_ORDER)
            fig = plot.get_figure()
            plot.set_xticklabels(plot.get_xticklabels(), rotation=90)
            plot.set_ylim([0, y_max])
            plot.grid(axis='y')
            fig.savefig(os.path.join(plot_path, '{}={}_swarmplot_{}.png'.format(SPLIT_ANALYSIS_COLUMN, groupname, relevant_col)))
            plt.clf()

            # bar plot
            reduced_df = df.groupby(relevant_col)[TARGET_COLUMN].describe()
            if VAR_ORDER is not None:
                reduced_df = reduced_df.loc[VAR_ORDER]
            reduced_df.plot.bar(y='mean', yerr='std')
            plt.ylim([0, y_max])
            plt.savefig(os.path.join(plot_path, '{}={}_barplot_{}.png'.format(SPLIT_ANALYSIS_COLUMN, groupname, relevant_col)))
            plt.clf()

        elif len(RELEVANT_PARAMETERS) > 1:
            # average over runs with same parameters
            df = df[RELEVANT_PARAMETERS + [TARGET_COLUMN]]
            df = df.groupby(RELEVANT_PARAMETERS, as_index=False).agg(np.mean)
            print("Best entry:")
            if LOWER_IS_BETTER:
                print(df.iloc[df[TARGET_COLUMN].idxmin()])
            else:
                print(df.iloc[df[TARGET_COLUMN].idxmax()])
            parallel_coordinates(df, TARGET_COLUMN, lower_is_better=LOWER_IS_BETTER)
            plt.savefig(os.path.join(plot_path, '{}={}_parallel_coordinates.svg'.format(SPLIT_ANALYSIS_COLUMN, groupname)))
