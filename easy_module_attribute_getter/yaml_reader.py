import argparse
from types import SimpleNamespace
from . import utils as c_f
import re
import yaml
from io import StringIO
import os
from collections import defaultdict


class YamlReader:
    def __init__(self, argparser=None, 
                force_override_key_word="~OVERRIDE~", 
                apply_key_word="~APPLY~",
                delete_key_word = "~DELETE~",
                swap_key_word = "~SWAP~"):
        self.argparser = argparser if argparser is not None else argparse.ArgumentParser(allow_abbrev=False)
        self.args, self.unknown_args = self.argparser.parse_known_args()
        if argparser is not None:
            self.validate_command_line_input()
            self.add_unknown_args()
        self.force_override_key_word = force_override_key_word
        self.apply_key_word = apply_key_word
        self.delete_key_word = delete_key_word
        self.swap_key_word = swap_key_word

    def validate_command_line_input(self):
        char_counts = defaultdict(int)
        colon_followed_by_char = re.compile(":[\s\S]")
        error_message = ""
        for u in self.unknown_args:
            colon_error = colon_followed_by_char.search(u)
            if colon_error:
                error_message += "There must be a space after the colon in this expression: \"{}\"\n".format(u)
            for char in ['{', '}', '[', ']', '(', ')']:
                char_counts[char] += u.count(char)
        should_be_balanced = [('{', '}'), ('[', ']'), ('(', ')')]
        for opener, closer in should_be_balanced:
            num_openers, num_closers = char_counts[opener], char_counts[closer]
            if num_openers != num_closers:
                error_message += "Command line bracket imbalance: {} of {} and {} of {}\n".format(num_openers, opener, num_closers, closer)
        error_message += self.add_unknown_args(dummy_run=True)       
        if error_message != "":
            raise ValueError(error_message)

    def bracket_parser(self, B, curr_flag, in_str, dummy_run=False):
        # B is the bracket dict
        attribute_is_set = False
        B["depth"] += in_str.count(B["opener"]) - in_str.count(B["closer"])
        B["is_start"] = in_str[0] == B["opener"]
        B["is_end"] = in_str[-1] == B["closer"]
        if B["is_start"] or B["is_end"] or (B["curr_value"] != ''):
            B["curr_value"] += ' %s' % in_str
        if B["is_end"] and B["depth"] == 0:
            if not dummy_run:
                setattr(self.args, curr_flag, yaml.load(StringIO(B["curr_value"]), yaml.SafeLoader))
            B["curr_value"] = ''
            curr_flag = None
            attribute_is_set = True
        return attribute_is_set, curr_flag


    def add_unknown_args(self, dummy_run=False):
        error_message = ""
        curr_flag = None
        depths = {"dict": {"opener": "{", "closer": "}", "depth": 0, "is_start": False, "is_end": False, "curr_value": ''}, 
                "list": {"opener": "[", "closer": "]", "depth": 0, "is_start": False, "is_end": False, "curr_value": ''}}
        D = depths["dict"]
        L = depths["list"]
        for u in self.unknown_args:
            if re.match("^--[a-zA-Z]", u) is not None:
                curr_flag = u[2:]
                if not dummy_run:
                    setattr(self.args, curr_flag, True)
            else:
                if L["curr_value"] == '':
                    attribute_is_set, curr_flag = self.bracket_parser(D, curr_flag, u, dummy_run)
                    if attribute_is_set:
                        continue
                if D["curr_value"] == '':
                    attribute_is_set, curr_flag = self.bracket_parser(L, curr_flag, u, dummy_run)
                    if attribute_is_set:
                        continue
                if (L["curr_value"] == '') and (D["curr_value"] == ''):
                    if not dummy_run:
                        setattr(self.args, curr_flag, yaml.load(StringIO(u), yaml.SafeLoader))
                    elif curr_flag == None:
                        error_message += "{} is missing \"--\" in front of it. If you meant to pass in a list, use standard python list notation.\n".format(u) 
                    curr_flag = None
        return error_message


    def load_yamls(self, config_paths=None, root_path=None, max_merge_depth=0,  max_argparse_merge_depth=0, merge_argparse=True):
        self.dict_of_yamls = defaultdict(dict)
        for config_name, config_list in config_paths.items():
            for c in config_list:
                curr_yaml = c_f.load_yaml(c)
                curr_yaml = c_f.merge_two_dicts(self.dict_of_yamls[config_name], 
                                                curr_yaml, 
                                                max_merge_depth=max_merge_depth,
                                                force_override_key_word=self.force_override_key_word,
                                                apply_key_word=self.apply_key_word,
                                                delete_key_word=self.delete_key_word,
                                                swap_key_word=self.swap_key_word)
                if merge_argparse:
                    curr_yaml = c_f.merge_two_dicts(curr_yaml, 
                                                    self.args.__dict__, 
                                                    max_merge_depth=max_argparse_merge_depth, 
                                                    only_existing_keys=True, 
                                                    force_override_key_word=self.force_override_key_word,
                                                    apply_key_word=self.apply_key_word,
                                                    delete_key_word=self.delete_key_word,
                                                    swap_key_word=self.swap_key_word)

                self.dict_of_yamls[config_name] = curr_yaml
        
        self.loaded_yaml = {}
        for config in self.dict_of_yamls.values():
            self.loaded_yaml = c_f.merge_two_dicts(self.loaded_yaml, config, max_merge_depth=0)

        for key_word in [self.force_override_key_word, self.apply_key_word, self.delete_key_word, self.swap_key_word]:
            c_f.remove_key_word_recursively(self.args.__dict__, key_word)

        self.args = c_f.merge_two_dicts(self.loaded_yaml, 
                                        self.args.__dict__, 
                                        max_merge_depth=max_argparse_merge_depth, 
                                        only_non_existing_keys=True, 
                                        force_override_key_word=self.force_override_key_word,
                                        apply_key_word=self.apply_key_word,
                                        delete_key_word=self.delete_key_word,
                                        swap_key_word=self.swap_key_word)
        self.args = SimpleNamespace(**self.args)

        return self.args, self.loaded_yaml, self.dict_of_yamls