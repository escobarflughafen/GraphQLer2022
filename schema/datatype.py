class Datatype:
    def __init__(self, schema_json=None ,sdl=None):
        if schema_json or sdl:
            if schema_json:
                pass
            else:
                pass
        else:
            raise Exception("no datatype definition is provided")