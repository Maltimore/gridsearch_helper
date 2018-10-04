import os
import uuid
import itertools
from ruamel.yaml import YAML
import sys

project_dir_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(project_dir_file_path)
import main

yaml = YAML()

task_id = int(os.environ['SGE_TASK_ID'])
print("In python_entry.py, task_id is {}".format(task_id))


def assign_gridsearch_hyperparameters(id_, params):
    """assign_hyperparameters
    Maps an index to a hyperparameter combination. In params, values that are lists
    are interpreted to be those for which different combinations should be tested.

    :param id_: scalar, indicates whic parameter combination to assign
    :param params: dict holding the hyperparameters.
    :returns params: returns a copy of params with list-values replaced by
        list items corresponding to the relevant hyperparameter combination.
    """
    params = params.copy()
    gridsearch_params = params['gridsearch']
    params = params['default']
    # the following determines how many parameter combos there are, based on the number
    # of lists in params. It then selects the parameter combo based on task_id
    param_names = []
    param_values = []
    for key in gridsearch_params.keys():
        param_names.append(key)
        param_values.append(gridsearch_params[key])
    # get all parameter combinations with the cartesian product
    parametercombos = list(itertools.product(*param_values))
    parametercombo_id = (id_ - 1) % len(parametercombos)
    parametercombo = parametercombos[parametercombo_id]
    for idx, key in enumerate(param_names):
        params[key] = parametercombo[idx]
    return params


params_path = os.path.join(project_dir_file_path, 'parameters.yaml')
with open(params_path, 'r') as f:
    params = dict(yaml.load(f))
params = assign_gridsearch_hyperparameters(task_id, params)

random_run_id = str(uuid.uuid1())
print('Random run ID is: {}'.format(random_run_id))

output_path = os.path.join(
    'outfiles',
    str(os.environ['JOB_NAME']),
    'full_outputs',
    str(task_id).zfill(4) + '_' + random_run_id,
)
gridsearch_results_path = os.path.join(
    'outfiles',
    str(os.environ['JOB_NAME']),
    'results',
    str(task_id).zfill(4) + '_' + random_run_id,
)
if not os.path.exists(output_path):
    os.makedirs(output_path)
if not os.path.exists(gridsearch_results_path):
    os.makedirs(gridsearch_results_path)

params['output_path'] = output_path
params['gridsearch_results_path'] = gridsearch_results_path
params['gridsearch'] = True

# dump selected params
with open(os.path.join(gridsearch_results_path, 'parameters.yaml'), 'w') as f:
    yaml.dump(params, f)

print(params)
print("Running main.main()")
main.main(params)
