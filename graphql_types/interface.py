from graphql_types import datatype
from graphql_types.obj import Object

class Interface(datatype.Datatype):
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )
    
    def is_interface_of(self, obj):
        return self.schema["name"] in obj.schema["interfaces"] 
        
