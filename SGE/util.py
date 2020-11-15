import time
#start_time = time.time()
#print("Start time: {}".format(
#    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time))))
import os
import itertools
import platform
import subprocess
import warnings
import copy


def flatten_dict(thed):
    thed = copy.deepcopy(thed)
    to_flatten = {}
    for key in thed.keys():
        if isinstance(thed[key], dict):
            flattened = flatten_dict(thed[key])
            for key2 in flattened.keys():
                to_flatten[(key,) + key2] = flattened[key2]
        else:
            to_flatten[(key,)] = thed[key]
    return to_flatten


def assign_hyperparams(id_, params):
    """assign_hyperparameters
    Maps an index to a hyperparameter combination. In params, values that are lists
    are interpreted to be those for which different combinations should be tested.

    :param id_: scalar, indicates whic parameter combination to assign
    :param params: dict holding the hyperparameters.
    :returns params: returns a copy of params with list-values replaced by
        list items corresponding to the relevant hyperparameter combination.
    """
    gridsearch_params = params['gridsearch']
    flattened_gridsearch_params = flatten_dict(gridsearch_params)
    param_combo = list(itertools.product(*flattened_gridsearch_params.values()))[id_ - 1]
    for key_idx, key in enumerate(flattened_gridsearch_params.keys()):
        if len(key) == 2:
            params['default'][key[1]] = param_combo[key_idx]
        else:
            subdict = params['default'][key[1]]
            for subkey in key[2:-1]:
                subdict = subdict[subkey]
            subdict[key[-1]] = param_combo[key_idx]
    return params
    # The following determines how many parameter combos there are
    # It then selects the parameter combo based on task_id
#    while True:
#        for config in gridsearch_params.keys():
#            param_names, param_values = zip(*gridsearch_params[config].items())
#            # get all parameter combinations with the cartesian product
#            parametercombos = list(itertools.product(*param_values))
#            if (id_ - 1) < len(parametercombos):
#                parametercombo = parametercombos[id_ - 1]
#                for idx, key in enumerate(param_names):
#                    params[key] = parametercombo[idx]
#                return params
#            id_ -= len(parametercombos)


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


def get_run_info():
    task_id = int(os.environ['SGE_TASK_ID'])
    run_info = {
        "start_time": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time)),
        "git_hash": get_git_info()["git_hash"],
        "git_status": get_git_info()["git_status"],
        "gridsearch": True,
        "hostname": platform.uname()[1],
        "run_finished": False,
        "task_id": task_id,
    }
    return run_info

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
