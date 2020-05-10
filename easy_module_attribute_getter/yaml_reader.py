import argparse
from types import SimpleNamespace
from . import utils as c_f
import re
import yaml
from io import StringIO
import os


class YamlReader:
    def __init__(self, argparser=None, force_override_key_word="~OVERRIDE~"):
        self.argparser = argparser if argparser is not None else argparse.ArgumentParser(allow_abbrev=False)
        self.args, self.unknown_args = self.argparser.parse_known_args()
        if argparser is not None:
            self.add_unknown_args()
        self.force_override_key_word = force_override_key_word

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

    def load_yamls(self, config_paths=None, root_path=None, subfolder_to_name_dict=None, max_merge_depth=0, merge_argparse=True):
        self.loaded_yaml = {}
        self.dict_of_yamls = {}
        if config_paths:
            path_list = config_paths
        else:
            path_list = [os.path.join(root_path, k, '%s.yaml'%v) for k, v in subfolder_to_name_dict.items()]
        for c in path_list:
            curr_yaml = c_f.load_yaml(c)
            if merge_argparse:
                curr_yaml = c_f.merge_two_dicts(curr_yaml, self.args.__dict__, max_merge_depth=max_merge_depth, only_existing_keys=True, force_override_key_word=self.force_override_key_word)
            self.dict_of_yamls[c] = curr_yaml
            self.loaded_yaml = c_f.merge_two_dicts(self.loaded_yaml, curr_yaml, max_merge_depth=max_merge_depth, force_override_key_word=self.force_override_key_word)
        c_f.remove_key_word_recursively(self.args.__dict__, self.force_override_key_word)
        self.args = c_f.merge_two_dicts(self.loaded_yaml, self.args.__dict__, max_merge_depth=max_merge_depth, only_non_existing_keys=True, force_override_key_word=self.force_override_key_word)
        self.args = SimpleNamespace(**self.args)
        return self.args, self.loaded_yaml, self.dict_of_yamls