from graphql_types import datatype
from introspection import parse


class Enum(datatype.Datatype):
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )
    
    
    def values(self):
        return [enum_entry["name"] for enum_entry in self.schema["values"]]
    