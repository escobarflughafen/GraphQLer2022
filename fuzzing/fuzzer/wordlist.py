import sys, os, random
import sys
import os
import random
from fuzzing.fuzzer.fuzzer import Fuzzer
from fuzzing.fuzzer.configs.constant_dict import default_constants

def add_escape_backslash(string):
    escapestr = ''

    for ch in string:
        if ch == '"':
            escapestr += '\\"'
        elif ch == '\\':
            escapestr += '\\\\'
        else:
            escapestr += ch

    return escapestr


class WordlistFuzzer(Fuzzer):

    def __init__(self, schema, cache, wordlists):
        super().__init__(schema, cache)
        self.wordlists = [add_escape_backslash(w).replace('\n', '') for w in wordlists]

    def resolve_int(self, arg):
            return default_constants['Int']

    def resolve_float(self, arg):
            return default_constants['Float']

    def resolve_string(self, arg):
        return self.wordlists[random.randint(0, len(self.wordlists)-1)]

    def resolve_enum(self, arg):
        enum_schema = self.schema["enums"]

        enum_oftype = enum_schema[arg["kind"]]
        enum_values = [v["name"] for v in enum_oftype["values"]]

        return enum_values[random.randint(0, len(enum_values)-1)]
        