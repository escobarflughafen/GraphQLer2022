import sys, os, random
from fuzzing.fuzzer.fuzzer import Fuzzer

default_constants = {
    'Int': 1,
    'Float': 1.1,
    'String': 'teststring',
    'Enum': 0
}

class RandomFuzzer(Fuzzer):
    def __init__(self, schema, cache):
        super().__init__(schema, cache)

    def resolve_int(self, arg):
        try:
            return random.randint(0, 2**32-1)
        except Exception:
            return default_constants['Int']

    def resolve_float(self, arg):
        try:
            return random.random() * (2**32-1)
        except Exception:
            return default_constants['Float']

    def resolve_string(self, arg):
        length = random.randint(1, 1000)
        string = ""
        for i in range(length):
            string += chr(random.randint(0x20, 0x7E))
        
        return string

    def resolve_enum(self, arg):
        enum_schema = self.schema["enums"]

        enum_oftype = enum_schema[arg["kind"]]
        enum_values = [v["name"] for v in enum_oftype["values"]]
        
        wordlist_value = self.wordlists["Enum"].readline()
        
        if wordlist_value not in enum_values:
            return enum_values[default_constants['Enum']]

        return self.wordlists["Enum"].readline()
    