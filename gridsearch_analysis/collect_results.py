import pandas as pd
from ruamel.yaml import YAML
import os
import argparse

yaml = YAML()


def collect_results(path, default_values={}, result_keys=(), skip_unfinished_runs=True):
    """collect_results
    Goes through all the results directories, reads the parameters.yaml and program_state.yaml
    and writes the relevant values into a pandas dataframe

    :param path: str
        path to directory in which the result directories are
    :param default_values: dict containing default values for values missing or None
        in program_state.yaml
    """
    result_dirs = os.listdir(path)
    params_path = os.path.join(path, result_dirs[0], 'parameters.yaml')
    with open(params_path, 'r') as f:
        params = dict(yaml.load(f))
        df = pd.DataFrame()

    for idx, dir_ in enumerate(result_dirs):
        params_path = os.path.join(path, dir_, 'parameters.yaml')
        program_state_path = os.path.join(path, dir_, 'program_state.yaml')

        if not os.path.exists(params_path):
            print('Skipping {}.. because no params file'.format(dir_[:15]))
            continue
        if not os.path.exists(program_state_path):
            print('Skipping {}.. because no program_state file'.format(dir_[:15]))
            continue

        with open(program_state_path) as f:
            program_state = dict(yaml.load(f))

        if not program_state['run_finished'] and skip_unfinished_runs:
            print('Skipping {} because run didn\'t finish.'.format(dir_))
            continue

        if not program_state['run_finished']:
            for result_key in result_keys:
                if program_state[result_key] is None and result_key in default_values.keys():
                    program_state[result_key] = default_values[result_key]
                else:
                    print(('Skipping {} because run didn\'t finish and no '
                           'default values for {}').format(dir_))
                    continue

        with open(params_path, 'r') as f:
            params = dict(yaml.load(f))

        new_row = pd.Series(params)
        for result_key in result_keys:
            new_row[result_key] = program_state[result_key]
        df = df.append(new_row, ignore_index=True)
        if idx % 100 == 0:
            print("{} of {} done".format(str(idx).zfill(4), str(len(result_dirs)).zfill(4)))

    return df


if __name__ == '__main__':
    ##############################################################################################
    # default values are being used if the run didn't finish yet and skip_unfinished_runs is False
    DEFAULT_VALUES = {}
    DEFAULT_VALUES['first_success'] = 150
    RESULT_KEYS = ('first_success',)
    skip_unfinished_runs = True
    ##############################################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='results directory')
    args = parser.parse_args()
    results_path = os.path.join(args.path, 'results')
    df = collect_results(results_path, DEFAULT_VALUES, RESULT_KEYS, skip_unfinished_runs)
    df.to_csv(os.path.join(args.path, 'results_df.csv'))
