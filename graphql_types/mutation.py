from graphql_types import callable as _callable
from introspection import parse

class Mutation(_callable.Callable):
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )

        
