from . import datatype
from ..introspection import parse

class Mutation(datatype.Datatype):
    def __init__(self, schema_json=None ,sdl=None):
        super.__init__(schema_json, sdl)
        if schema_json:
            self.schema = schema_json
        elif sdl:
            self.__build_with_sdl(sdl) 


    def __build_with_sdl(self, sdl):
        pass

    def request(self, url, **args):
        f'''
        '''
        pass