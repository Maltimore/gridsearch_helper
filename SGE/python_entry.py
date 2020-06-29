import time
start_time = time.time()
print("Start time: {}".format(
    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time))))
import os
import uuid
import itertools
from ruamel.yaml import YAML
import sys

# the content of sys.argv[1] is the directory of the desired main.py file
main_dot_py_dir = sys.argv[1]
sys.path.append(main_dot_py_dir)
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
    # The following determines how many parameter combos there are
    # It then selects the parameter combo based on task_id
    while True:
        for config in gridsearch_params.keys():
            param_names, param_values = zip(*gridsearch_params[config].items())
            # get all parameter combinations with the cartesian product
            parametercombos = list(itertools.product(*param_values))
            if (id_ - 1) < len(parametercombos):
                parametercombo = parametercombos[id_ - 1]
                for idx, key in enumerate(param_names):
                    params[key] = parametercombo[idx]
                return params
            id_ -= len(parametercombos)


params_path = os.path.join(main_dot_py_dir, 'parameters.yaml')
with open(params_path, 'r') as f:
    params = dict(yaml.load(f))
params = assign_gridsearch_hyperparameters(task_id, params)

run_id = str(uuid.uuid1())
print('Random run ID is: {}'.format(run_id))

# create output paths and corresponding directories
gridsearch_root_output_dir = os.path.join(os.getcwd(), 'outfiles', str(os.environ['JOB_NAME']))
output_path = os.path.join(
    gridsearch_root_output_dir,
    str(task_id).zfill(4) + '_' + run_id,
)
if not os.path.exists(output_path):
    os.makedirs(output_path)

program_state = {
    "output_path": output_path,
    "gridsearch": True
}

# dump selected params and program_state
with open(os.path.join(output_path, 'parameters.yaml'), 'w') as f:
    yaml.dump(params, f)
with open(os.path.join(output_path, 'program_state.yaml'), 'w') as f:
    yaml.dump(program_state, f)

print("Parameters:")
print(params)
print("Running main.main()", flush=True)
main.main(params, program_state)

end_time = time.time()
run_time = end_time - start_time
print("End time: {}".format(
    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(end_time))))
print("Run time (seconds): {}".format(run_time), flush=True)
