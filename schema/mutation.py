from . import datatype
from ..introspection import parse

class Mutation(datatype.Datatype):
    def __init__(self, name, schema_json=None , introspection_json=None, sdl=None):
        super().__init__(name, schema_json=schema_json, sdl=sdl)

    def request(self, url, fields, **args):
        query = f'''
                    {self.name} { f"({''.join})" if args else "" } {{
                            {'\n'.join(fields)}
                    }}
                '''