import argparse
from types import SimpleNamespace
from . import utils as c_f
import re
import yaml
from io import StringIO
import os
from collections import defaultdict


class YamlReader:
    def __init__(self, argparser=None, force_override_key_word="~OVERRIDE~"):
        self.argparser = argparser if argparser is not None else argparse.ArgumentParser(allow_abbrev=False)
        self.args, self.unknown_args = self.argparser.parse_known_args()
        if argparser is not None:
            self.validate_command_line_input()
            self.add_unknown_args()
        self.force_override_key_word = force_override_key_word

    def validate_command_line_input(self):
        char_counts = defaultdict(int)
        colon_followed_by_char = re.compile(":[\s\S]")
        error_message = ""
        syntax_error = False
        for u in self.unknown_args:
            colon_error = colon_followed_by_char.search(u)
            if colon_error:
                syntax_error = True
                error_message += "There must be a space after the colon in this expression: \"{}\"\n".format(u)
            for char in ['{', '}', '[', ']', '(', ')']:
                char_counts[char] += u.count(char)
        should_be_balanced = [('{', '}'), ('[', ']'), ('(', ')')]
        for opener, closer in should_be_balanced:
            num_openers, num_closers = char_counts[opener], char_counts[closer]
            if num_openers != num_closers:
                syntax_error = True
                error_message += "Command line bracket imbalance: {} of {} and {} of {}\n".format(num_openers, opener, num_closers, closer)
        if syntax_error:
            raise ValueError(error_message)
        
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

    def load_yamls(self, config_paths=None, root_path=None, max_merge_depth=0, merge_argparse=True):
        self.dict_of_yamls = defaultdict(dict)
        for config_name, config_list in config_paths.items():
            for c in config_list:
                curr_yaml = c_f.load_yaml(c)
                if merge_argparse:
                    curr_yaml = c_f.merge_two_dicts(curr_yaml, 
                                                    self.args.__dict__, 
                                                    max_merge_depth=max_merge_depth, 
                                                    only_existing_keys=True, 
                                                    force_override_key_word=self.force_override_key_word)

                self.dict_of_yamls[config_name] = c_f.merge_two_dicts(self.dict_of_yamls[config_name], 
                                                                        curr_yaml, 
                                                                        max_merge_depth=max_merge_depth,
                                                                        force_override_key_word=self.force_override_key_word)
        
        self.loaded_yaml = {}
        for config in self.dict_of_yamls.values():
            self.loaded_yaml = c_f.merge_two_dicts(self.loaded_yaml, config, max_merge_depth=0)

        c_f.remove_key_word_recursively(self.args.__dict__, self.force_override_key_word)
        self.args = c_f.merge_two_dicts(self.loaded_yaml, 
                                        self.args.__dict__, 
                                        max_merge_depth=max_merge_depth, 
                                        only_non_existing_keys=True, 
                                        force_override_key_word=self.force_override_key_word)
        self.args = SimpleNamespace(**self.args)
        return self.args, self.loaded_yaml, self.dict_of_yamls