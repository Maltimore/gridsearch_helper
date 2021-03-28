import copy


def flatten_dict(dictionary, flatten_key_method='tuple'):
    """
    This function recursively flattens an arbitrarily nested
    dictionary.
    The keys into the flattened dictionary are tuples of the form
    (key0, key1, key2..)
    """
    dictionary = copy.deepcopy(dictionary)
    to_flatten = {}
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            flattened = flatten_dict(dictionary[key], flatten_key_method=flatten_key_method)
            for key2 in flattened.keys():
                if flatten_key_method == 'tuple':
                    to_flatten[(key,) + key2] = flattened[key2]
                elif flatten_key_method in ['/', '-', '_']:
                    to_flatten[key + flatten_key_method + key2] = flattened[key2]
        else:
            if flatten_key_method == 'tuple':
                to_flatten[(key,)] = dictionary[key]
            elif flatten_key_method in ['/', '-', '_']:
                to_flatten[key] = dictionary[key]
    return to_flatten
