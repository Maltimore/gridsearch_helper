import time
start_time = time.time()
print("Start time: {}".format(
    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time))))
import os
import pathlib
import sys
import itertools
from ruamel.yaml import YAML
import platform
import subprocess
import warnings


output_path = sys.argv[1]
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


def get_git_info():
    try:
        return_dict = {
            "git_hash": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip('\n'),
            "git_status":  subprocess.check_output(['git', 'status']).decode('utf-8'),
        }
    except Exception:
        warnings.warn('\nWarning! Failed to get git revision hash!\n')
        return_dict = {
            "git_hash": "failed_to_get",
            "git_status": "failed_to_get"
        }
    return return_dict


params = yaml.load("parameters.yaml")
params = assign_gridsearch_hyperparameters(task_id, params)

yaml.dump(params, pathlib.Path(output_path, 'parameters.yaml'))

run_info = {
    "start_time": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time)),
    "output_path": output_path,
    "git_hash": get_git_info()["git_hash"],
    "git_status": get_git_info()["git_status"],
    "gridsearch": True,
    "hostname": platform.uname()[1],
    "run_finished": False,
    "task_id": task_id,
}
yaml.dump(run_info, pathlib.Path(output_path, 'run_info.yaml'))

#print("Parameters:")
#print(params)
#print("Running main.main()", flush=True)
#main.main(params, program_state)
#
#end_time = time.time()
#run_time = end_time - start_time
#print("End time: {}".format(
#    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(end_time))))
#print("Run time (seconds): {}".format(run_time), flush=True)
#
#program_state["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(end_time))
#program_state["run_time"] = time.strftime('%H:%M:%S', time.gmtime(run_time))
#program_state["run_finished"] = True
