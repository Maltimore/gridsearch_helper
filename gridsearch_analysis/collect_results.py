import pandas as pd
import yaml
import os

from . import util


def collect_results(path):
    """collect_results
    Goes through all directories found in path, reads the
    parameters.yaml, program_state.yaml and run_info.yaml and writes
    the relevant values into a pandas dataframe

    :param path: str
        path to directory in which the result directories are
    """
    result_dirs = os.listdir(path)
    df = pd.DataFrame()

    n_collected = 0
    for idx, dir_ in enumerate(sorted(result_dirs)):
        params_path = os.path.join(path, dir_, 'parameters.yaml')
        run_info_path = os.path.join(path, dir_, 'run_info.yaml')
        program_state_path = os.path.join(path, dir_, 'program_state.yaml')
        if not os.path.exists(params_path):
            print(f'Skipping {dir_} because no params file')
            continue
        if not os.path.exists(run_info_path):
            print(f'Skipping {dir_} because no run_info file')
            continue
        if not os.path.exists(program_state_path):
            print('Skipping {}.. because no program_state file'.format(
                dir_[:15]))
            continue

        with open(run_info_path) as f:
            run_info = dict(yaml.safe_load(f))
        with open(params_path) as f:
            params = dict(yaml.safe_load(f))
        with open(program_state_path) as f:
            program_state = dict(yaml.safe_load(f))

        new_row = pd.concat([
            pd.Series(util.flatten_dict(params['default'], flatten_key_method='/')),
            pd.Series(util.flatten_dict(run_info, flatten_key_method='/')),
            pd.Series(util.flatten_dict(program_state, flatten_key_method='/')),
            pd.Series({'output_dir': dir_}),
        ])
        # drop duplicated entries
        new_row = new_row[~new_row.index.duplicated(keep='last')]
        df = df.append(new_row, ignore_index=True)

        n_collected += 1

        if idx % 100 == 0:
            print("{} of {} done".format(
                str(idx).zfill(5),
                str(len(result_dirs)).zfill(5)))

    print(f"Collected {n_collected} out of {idx+1} runs")
    return df
