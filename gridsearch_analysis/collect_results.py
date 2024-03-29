import pandas as pd
import yaml
import os

import util


def collect_results(path):
    """collect_results
    Goes through all directories found in path, reads the
    parameters.yaml, results.yaml and run_info.yaml and writes
    the relevant values into a pandas dataframe

    :param path: str
        path to directory in which the result directories are
    """
    path = os.path.expanduser(path)
    df = None

    result_dirs = os.listdir(path)
    n_collected = 0
    for idx, dir_ in enumerate(sorted(result_dirs)):
        params_path = os.path.join(path, dir_, 'parameters.yaml')
        run_info_path = os.path.join(path, dir_, 'run_info.yaml')
        results_path = os.path.join(path, dir_, 'results.yaml')
        if not os.path.exists(params_path):
            print(f'Skipping folder {dir_} because no params file at {params_path}')
            continue
        if not os.path.exists(run_info_path):
            print(f'Skipping {dir_} because no run_info file at {run_info_path}')
            continue
        if not os.path.exists(results_path):
            print(f'Skipping {dir_}.. because no results file at {results_path}')
            continue

        with open(run_info_path) as f:
            run_info = dict(yaml.safe_load(f))
        with open(params_path) as f:
            params = dict(yaml.safe_load(f))
        with open(results_path) as f:
            results = dict(yaml.safe_load(f))

        new_row = pd.DataFrame(pd.concat([
            pd.Series(util.flatten_dict(params, flatten_key_method='/')),
            pd.Series(util.flatten_dict(run_info, flatten_key_method='/')),
            pd.Series(util.flatten_dict(results, flatten_key_method='/')),
            pd.Series({'output_dir': dir_}),
        ]))
        # drop duplicated entries
        new_row = new_row[~new_row.index.duplicated(keep='last')]
        if df is None:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True, axis=1)

        n_collected += 1

        if idx % 100 == 0:
            print("{} of {} done".format(
                str(idx).zfill(5),
                str(len(result_dirs)).zfill(5)))

    print(f"Collected {n_collected} out of {idx+1} runs")
    df = df.transpose()
    return df
