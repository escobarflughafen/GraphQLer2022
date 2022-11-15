from . import datatype

class Mutation(datatype.Datatype):
    def __init__(self, schema_json=None ,sdl=None):
        super.__init__(schema_json, sdl)