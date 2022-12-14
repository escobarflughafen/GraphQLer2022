from introspection import parse

class Datatype:
    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        self.name = name
        if schema_json or introspection_json or sdl:
            if schema_json:
                self.schema = schema_json
            elif introspection_json:
                self.__build_with_introspection_json(introspection_json)
            elif sdl:
                self.__build_with_sdl(sdl)
        else:
            raise Exception("no datatype definition is provided")

    def __build_with_introspection_json(self, introspection_json):
        self.schema = parse.SchemaBuilder(introspection_json=introspection_json).schema

    def __build_with_sdl(self, sdl):
        self.schema = {}
    
