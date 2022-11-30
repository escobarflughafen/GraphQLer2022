import sys, os, random

STATIC_TYPES = [{'kind'}]
DYNAMIC_TYPES = [{'kind': 'SCALAR', 'name': 'ID'}, {'kind': 'INPUT_OBJECT'}]


class Fuzzer:
    
    def __init__(self, schema, fuzzables, static_types, dynamic_types, cache, max_depth):
        self.fuzzables = fuzzables
        self.static_types = static_types
        self.dynamic_types = dynamic_types
        self.cache = cache
        self.max_depth = max_depth
        self.schema = schema
    
    def set_max_depth(self, n):
        if n <= 0:
            raise "set n greater than 0" 
        self.max_depth = n
    
    def handle_static_arg(self, arg):
        '''
            override this method in implementations
        '''

        raise "no default handling for static argument is defined"

    def handle_dynamic_arg(self, arg):
        return self.cache.get_random_object(arg["object_type"])

    def concretize_payload(self, args):
        for argname, value in args.items():
            if isinstance(value, dict):
                self.concretize_payload(value)
            else:
                if value["type"] == "SCALAR" and ("id" in argname.lower()):
                    self.handle_dynamic_arg(value)
                else:
                    self.handle_static_arg(value)
