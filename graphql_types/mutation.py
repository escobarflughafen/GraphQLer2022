from graphql_types import datatype
from introspection import parse

class Mutation(datatype.Datatype):
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )

    def request(self, url, fields, **args):
        pass
        
        #query = f'''
                    #{self.name} (f"({','.join([f"{arg}: {args[arg]}" for arg in args])})" if args else "") {{
                            #{'\n'.join(fields)}
                    #}}
                #'''
        
