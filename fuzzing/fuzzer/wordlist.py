import sys, os, random
import sys
import os
import random
from fuzzing.fuzzer.fuzzer import Fuzzer

default_constants = {
    'Int': 1,
    'Float': 1.1,
    'String': 'teststring',
    'Enum': 0
}

class ConstantFuzzer(Fuzzer):

    def __init__(self, schema, cache, wordlists: dict):
        super().__init__(schema, cache)
        self.wordlists = {
            static_type: open(wordlist) for static_type, wordlist in wordlists.items()
        }

    def resolve_int(self, arg):
        try:
            return int(self.wordlists['Int'].readline())
        except Exception:
            return default_constants['Int']

    def resolve_float(self, arg):
        try:
            return float(self.wordlists['Float'].readline())
        except Exception:
            return default_constants['Float']

    def resolve_string(self, arg):
        return self.wordlists['String'].readline()

    def resolve_enum(self, arg):
        enum_schema = self.schema["enums"]

        enum_oftype = enum_schema[arg["kind"]]
        enum_values = [v["name"] for v in enum_oftype["values"]]
        
        wordlist_value = self.wordlists["Enum"].readline()
        
        if wordlist_value not in enum_values:
            return enum_values[default_constants['Enum']]

        return self.wordlists["Enum"].readline()
    