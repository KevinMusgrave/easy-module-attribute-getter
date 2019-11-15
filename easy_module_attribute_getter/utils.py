import yaml
import re


def load_yaml(fname):
    with open(fname, 'r') as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def merge_two_dicts(x, y, curr_depth=0, max_merge_depth=0, 
                    only_existing_keys=False, only_non_existing_keys=False,
                    force_override_key_word='~OVERRIDE~'):
    if curr_depth > max_merge_depth:
        return y
    z = x.copy()
    list_of_keys_to_add = []
    for key, v in y.items():
        # override z if the key ends with ~OVERRIDE~
        if key.endswith(force_override_key_word):
            k = re.sub('\%s$'%force_override_key_word, '', key)
            list_of_keys_to_add.append(k)
            force_override = True
        else:
            k = key
            force_override = False
        if (only_existing_keys and k in z) or (only_non_existing_keys and k not in z) or (not only_existing_keys and not only_non_existing_keys):  
            # merging 2 subdictionaries  
            if k in z and isinstance(z[k], dict) and isinstance(v, dict):
                if force_override:
                    z[k] = v
                else:   
                    z[k] = merge_two_dicts(z[k], v, curr_depth+1, max_merge_depth)   
            else: 
                z[k] = v
    for key in list_of_keys_to_add:
        y[key] = v
        del y[key+force_override_key_word]
    return z


def string_to_num(s):
    """
    If input is not a string, then return input.
    If input is a string, then try to convert to int,
    then try to convert to float.
    """
    if type(s) != str:
        return s
    try:
        return int(s)
    except BaseException:
        try:
            return float(s)
        except BaseException:
            return s


def try_convert_to_list_of_numbers(transform_params):
    """
    Args:
        transform_params: a dict mapping transform parameter names to values
    This function tries to convert each parameter value to a list of numbers.
    If that fails, then it tries to convert the value to a number.
    For example, if transform_params = {'scale':'0.16 1', size='256'}, this will become
    {'scale':[0.16, 1], 'size': 256}.
    """
    for k, v in transform_params.items():
        try:
            v = [string_to_num(x) for x in v.split(" ")]
            if len(v) == 1:
                v = v[0]
        except BaseException:
            v = string_to_num(v)
        transform_params[k] = v
    return transform_params
