from . import datatype
from ..introspection import parse

def build_query_string(json_string, dbdata = {}):
    inner_json = {}
    query = "{" + json_string["name"] + "("
    for arg in json_string["consumes"]:
        data_type = get_type(arg["type"])
        if data_type["kind"] == "SCALAR":
            inner_json[arg["name"]] = dbdata[arg["name"]] if dbdata.get(arg["name"]) != None else fuzz_scalar(data_type["name"])
        else:
            inner_json[arg["name"]] = build_object(search_object(data_type_json, data_type["name"]))
    # Remove the double quote for key but not the value (since GraphQL query did not like it)
    query += re.sub(r'(?<!: )"(\S*?)"', '\\1' ,json.dumps(inner_json)[1:-1]) + ")"
    
    data_type = get_type(json_string["produces"])
    if data_type["kind"] == "SCALAR":
        query += data_type["name"] + " " # it seems no SCALAR will exists in the first layer so this line will never run, anyways this line of code is broken
    else:
        query += build_return_object(search_object(data_type_json, data_type["name"]))

    query += "}"
    return query

class Query(datatype.Datatype):
    def __init__(self, name, schema_json=None , introspection_json=None, sdl=None):
        super().__init__(name, schema_json=schema_json, introspection_json=introspection_json, sdl=sdl)

    def request(self, url, fields, **args):
        query = f'''
                    {self.name} { f"({''.join([f'{arg}: {args[arg]}' for arg in args])})" if args else "" } {{
                            {'\n'.join(fields)}
                    }}
                '''