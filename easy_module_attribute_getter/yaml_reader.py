import argparse
from types import SimpleNamespace
from . import utils as c_f
import re
import yaml
from io import StringIO


class YamlReader:
    def __init__(self, argparser=None):
        self.argparser = argparser if argparser is not None else argparse.ArgumentParser()
        self.args, self.unknown_args = self.argparser.parse_known_args()
        self.add_unknown_args()

    def add_unknown_args(self):
        curr_flag = None
        curr_dictionary = ''
        dictionary_depth = 0
        for u in self.unknown_args:
            if re.match("^--[a-zA-Z]", u) is not None:
                curr_flag = u[2:]
                setattr(self.args, curr_flag, True)
            else:
                dictionary_depth += u.count('{') - u.count('}')
                is_start = u[0] == '{'
                is_end = u[-1] == '}'
                if (is_start or is_end) or (curr_dictionary != ''):
                    curr_dictionary += ' %s' % u
                if is_end and dictionary_depth == 0:
                    setattr(self.args, curr_flag, yaml.load(StringIO(curr_dictionary), yaml.SafeLoader))
                    curr_dictionary = ''
                    curr_flag = None
                # flag argument and not part of dictionary
                elif curr_dictionary == '':
                    setattr(self.args, curr_flag, yaml.load(StringIO(u), yaml.SafeLoader))
                    curr_flag = None

    def load_yamls(self, config_paths=None, root_path=None, subfolder_to_name_dict=None, max_merge_depth=0):
        self.loaded_yaml = {}
        self.dict_of_yamls = {}
        if config_paths:
            path_list = config_paths
        else:
            path_list = ['%s/%s/%s.yaml' % (root_path, k, v) for k, v in subfolder_to_name_dict.items()]
        for c in path_list:
            curr_yaml = c_f.merge_two_dicts(c_f.load_yaml(c), self.args.__dict__, max_merge_depth=max_merge_depth, only_existing_keys=True)
            self.dict_of_yamls[c] = curr_yaml
            self.loaded_yaml = c_f.merge_two_dicts(self.loaded_yaml, curr_yaml, max_merge_depth=max_merge_depth)
        self.args = c_f.merge_two_dicts(self.loaded_yaml, self.args.__dict__, max_merge_depth=max_merge_depth)
        self.args = SimpleNamespace(**self.args)
        return self.args, self.loaded_yaml, self.dict_of_yamls