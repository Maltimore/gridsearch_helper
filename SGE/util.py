import itertools
import copy


def flatten_dict(thed):
    """
    This function recursively flattens an arbitrarily nested dictionary.
    The keys into the flattened dictionary are tuples of the form
    (key0, key1, key2..)
    """
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
    param_combos = list(itertools.product(*flattened_gridsearch_params.values()))
    param_combo = param_combos[(id_ - 1) % len(param_combos)]
    for key_idx, key in enumerate(flattened_gridsearch_params.keys()):
        if len(key) == 2:
            params['default'][key[1]] = param_combo[key_idx]
        else:
            subdict = params['default'][key[1]]
            for subkey in key[2:-1]:
                subdict = subdict[subkey]
            subdict[key[-1]] = param_combo[key_idx]
    return params
