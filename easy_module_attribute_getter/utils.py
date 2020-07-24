import yaml
import re


def load_yaml(fname):
    with open(fname, 'r') as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml

def all_are_dicts(list_of_candidates):
    return all(isinstance(x, dict) for x in list_of_candidates)

def swap_keys(x, y):
    for k,v in y.items():
        if (v is not None) and (v != {}):
            if k in x:
                x[v] = x[k]
                x.pop(k)
        elif k not in x:
            assert len(x) == 1
            only_key = list(x.keys())[0]
            x[k] = x[only_key]
            x.pop(only_key)
    return x

def apply_to_dict(x, y, curr_depth, depth, swap=False):
    z = x.copy()
    if curr_depth == depth:
        if swap:
            return swap_keys(z,y)
        else:
            return merge_two_dicts(z, y)
    for k in z.keys():
        if isinstance(z[k], dict):
            z[k] = apply_to_dict(z[k], y, curr_depth+1, depth, swap=swap)
        elif (curr_depth + 1) == depth:
            if swap:
                z = swap_keys(z,y)
            else:
                z[k] = y
    return z


# Setting only_existing_keys to True only makes it apply to the top-level. 
# Same with only_non_existing_keys
def merge_two_dicts(x, y, curr_depth=0, max_merge_depth=0, 
                    only_existing_keys=False, only_non_existing_keys=False,
                    force_override_key_word='~OVERRIDE~',
                    apply_key_word='~APPLY~',
                    delete_key_word='~DELETE~',
                    swap_key_word='~SWAP~'):
    if curr_depth > max_merge_depth:
        return y
    z = x.copy()
    for key, v in y.items():
        force_override, apply, delete, swap = False, False, False, False
        apply_string = re.search("{}[0-9]+$".format(apply_key_word), key)
        swap_string = re.search("{}[0-9]+$".format(swap_key_word), key)
        # override z if the key ends with ~OVERRIDE~
        if key.endswith(force_override_key_word):
            k = re.sub('\%s$'%force_override_key_word, '', key)
            force_override = True
        elif apply_string:
            assert isinstance(v, dict), "The {} keyword can only be used on dictionaries".format(apply_key_word)
            apply_string = apply_string.group()
            k = re.sub('\%s$'%apply_string, '', key)
            apply_depth = int(apply_string.replace(apply_key_word, ""))
            assert apply_depth > 0
            apply = True
        elif swap_string:
            assert isinstance(v, dict), "The {} keyword can only be used on dictionaries".format(swap_key_word)
            swap_string = swap_string.group()
            k = re.sub('\%s$'%swap_string, '', key)
            swap_depth = int(swap_string.replace(swap_key_word, ""))
            assert swap_depth > 0
            swap = True
        elif key.endswith(delete_key_word):
            k = re.sub('\%s$'%delete_key_word, '', key)
            delete = True
        else:
            k = key
        if (only_existing_keys and k in z) or (only_non_existing_keys and k not in z) or (not only_existing_keys and not only_non_existing_keys):
            if delete:
                z.pop(k, None)
            # merging 2 subdictionaries  
            elif (not apply) and (not swap):
                if (k in z) and all_are_dicts([z[k], v]):
                    if force_override:
                        z[k] = v
                    else:   
                        z[k] = merge_two_dicts(z[k], v, curr_depth+1, max_merge_depth)   
                else:
                    z[k] = v
            # apply or swap is True. 
            # If apply, then merge v into z[k], at depth apply_depth
            # If swap, then replace the key at a swap_depth with v
            else:
                depth = apply_depth if apply else swap_depth
                if isinstance(z[k], dict):
                    z[k] = apply_to_dict(z[k], v, 1, depth, swap=swap)
    return z


def remove_key_word(input_dict, key_word):
    override_list = []
    for key, v in input_dict.items():
        key_word_with_number = re.search("{}[0-9]+$".format(key_word), key)
        if key.endswith(key_word):
            k = re.sub('\%s$'%key_word, '', key)
            override_list.append((key,k,v))
        elif key_word_with_number:
            key_word_with_number = key_word_with_number.group()
            k = re.sub('\%s$'%key_word_with_number, '', key)
            override_list.append((key,k,v))

    for (original_key, k, v) in override_list:
        input_dict[k] = v
        input_dict.pop(original_key, None)


def remove_key_word_recursively(args_dict, keyword):
    for v in args_dict.values():
        if isinstance(v, dict):
            remove_key_word(v, keyword)
            remove_key_word_recursively(v, keyword)
    remove_key_word(args_dict, keyword)


def remove_dicts(args_dict):
    remove_list = []
    for key, v in args_dict.items():
        if isinstance(v, dict):
            remove_list.append(key)
    for k in remove_list:
        args_dict.pop(k)


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
    except ValueError:
        try:
            return float(s)
        except ValueError:
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
        except AttributeError:
            v = string_to_num(v)
        transform_params[k] = v
    return transform_params
