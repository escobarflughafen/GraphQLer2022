import sys, os, random
from fuzzing import cache

STATIC_TYPES = [{'kind'}]
DYNAMIC_TYPES = [{'kind': 'SCALAR', 'name': 'ID'}, {'kind': 'INPUT_OBJECT'}]


class Fuzzer:
    def __init__(self, schema, cache: cache.Cache):
        self.cache = cache
        self.schema = schema
    
    def set_max_depth(self, n):
        if n <= 0:
            raise "set n greater than 0" 
        self.max_depth = n
    
    def resolve_int(self, arg):
        raise "no default handling for int argument is defined"
    
    def resolve_float(self, arg):
        raise "no default handling for float argument is defined"

    def resolve_string(self, arg):
        raise "no default handling for string argument is defined"

    def resolve_enum(self, arg):
        raise "no default handling for enum argument is defined"

    def resolve_boolean(self, arg):
        raise "no default handling for boolean argument is defined"

    def resolve_id(self, id_oftype):
        # TODO: resolve dynamic object
        # TODO: fetch dynamic id by config file & schema
        dynamic_id = self.cache.get_random_id_by_type(id_oftype)
        return dynamic_id    
