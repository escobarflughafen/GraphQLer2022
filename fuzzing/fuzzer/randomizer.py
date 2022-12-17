import sys, os, random
from fuzzing.fuzzer.fuzzer import Fuzzer
from fuzzing.fuzzer.configs.constant_dict import default_constants

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
        length = random.randint(1, 100)
        string = ""
        
        for i in range(length):
            char = chr(random.randint(0x20, 0x7E))
            if char == '"':
                char = '\\"'
            elif char == "\\":
                char = "\\\\"

            string += char
        
        return string

    def resolve_enum(self, arg):
        return None    

    def resolve_boolean(self, arg):
        return random.random() > 0.5
    