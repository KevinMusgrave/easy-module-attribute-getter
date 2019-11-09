import yaml


def load_yaml(fname):
    with open(fname, 'r') as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def merge_two_dicts(x, y, curr_depth=0, max_merge_depth=0, only_existing_keys=False):
    if curr_depth > max_merge_depth:
        return y
    z = x.copy()  # start with x's keys and values  
    for k, v in y.items():  
        if k in z and isinstance(z[k], dict) and isinstance(y[k], dict):   
            z[k] = merge_two_dicts(z[k], v, curr_depth+1, max_merge_depth) 
        elif not only_existing_keys:   
            z[k] = v    
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
