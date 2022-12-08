import sys
import os
import random
from fuzzing.fuzzer.fuzzer import Fuzzer


default_constants = {
    'Int': 1,
    'Float': 1.1,
    'String': 'teststring',
    'Enum': 0,
    "Boolean": True
}

class ConstantFuzzer(Fuzzer):

    def __init__(self, schema, cache, constants=default_constants):
        super().__init__(schema, cache)
        self.constants = constants

    def resolve_int(self, arg):
        return self.constants['Int']

    def resolve_float(self, arg):
        return self.constants['Float']

    def resolve_string(self, arg):
        return self.constants['String']

    def resolve_enum(self, arg):
        enum_schema = self.schema["enums"]

        enum_oftype = enum_schema[arg["kind"]]

        enum_value_index = self.constants["Enum"]

        return enum_oftype["values"][0]["name"]
    
    def resolve_boolean(self, arg):
        return self.constants["Boolean"]
