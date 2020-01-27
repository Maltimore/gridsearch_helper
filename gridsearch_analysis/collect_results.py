import pandas as pd
from ruamel.yaml import YAML
import os

yaml = YAML()


def collect_results(path):
    """collect_results
    Goes through all the results directories, reads the parameters.yaml and program_state.yaml
    and writes the relevant values into a pandas dataframe

    :param path: str
        path to directory in which the result directories are
    :param save_df_to: str or None, default None
        if not None, save the resulting df to this path
    """
    result_dirs = os.listdir(path)
    df = pd.DataFrame()

    for idx, dir_ in enumerate(sorted(result_dirs)):
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

        if not program_state['run_finished']:
            print('Skipping {} because run didn\'t finish.'.format(dir_))
            continue

        with open(params_path, 'r') as f:
            params = dict(yaml.load(f))

        new_row = pd.concat([pd.Series(params), pd.Series(program_state)])
        # it happens that the same value was saved in the program_state and
        # the parameters (it shouldn't happen, but it does). So drop one of them
        new_row = new_row[~new_row.index.duplicated()]
        df = df.append(new_row, ignore_index=True)


        if idx % 100 == 0:
            print("{} of {} done".format(str(idx).zfill(4), str(len(result_dirs)).zfill(4)))

    return df
