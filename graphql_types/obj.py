import sys
from graphql_types import datatype

class Object(datatype.Datatype):
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )
    
    def is_implemented_from(self, interface):
        return interface.is_interface_of(self)
    
    def cache():
        pass

    def consume():
        pass
        

