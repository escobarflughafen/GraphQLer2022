import sys
sys.path.append("../graphql_types")
from graphql_types import datatype

class Query(datatype.Datatype):
    def __init__(self, name, schema_json=None , introspection_json=None, sdl=None):
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

        #return query
        
