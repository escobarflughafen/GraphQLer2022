import connection
import json
import yaml
from pprint import pprint

all_types = {}

mock_mutation = json.load(open("./shopify_introspection.json"))
mutation_type_name = mock_mutation["data"]["__schema"]["mutationType"]["name"]

def get_name(raw_introspection):
    return raw_introspection["name"]


def get_type(typedef):
    if typedef["ofType"] == None:
        return {
            "kind": typedef["kind"],
            "name": typedef["name"]
        }
    else:
        # flatten one level of non-null wrapper
        kind = typedef["kind"]
        if kind == "NON_NULL":
            _type = get_type(typedef["ofType"])
            return {
                **_type,
                "nonNull": True
            }
        else:
            return {
                "kind": kind,
                "name": typedef["name"],
                "ofType": get_type(typedef["ofType"])
            }



def get_args(raw_introspection):
    args = []
    raw_args = raw_introspection["args"]
    for arg in raw_args:
        obj = {}
        obj["name"] = arg["name"]
        obj["type"] = get_type(arg["type"])
        obj["defaultValue"] = arg["defaultValue"]

        args.append(obj)
    return args


def get_return_type(raw_introspection):
    return raw_introspection["type"]


def get_action_type(args):
    has_input_field = False
    has_id_field = False
    for arg in args:
        if arg["type"]["kind"] == "SCALAR" and arg["type"]["name"] == "ID":
            has_id_field = True

        if arg["type"]["kind"] == "INPUT_OBJECT":
            has_input_field = True

    if has_input_field and has_id_field:
        return "UPDATE"

    if has_input_field and not has_id_field:
        return "CREATE"

    if not has_input_field and has_id_field:
        return "DELETE"

    return "OTHER"


class Mutation:
    def __init__(self, raw_introspection):
        self.name = get_name(raw_introspection)
        self.args = get_args(raw_introspection)
        self.return_type = get_return_type(raw_introspection)
        self.action_type = get_action_type(self.args)

    def to_dict(self):
        return {
            "name": self.name,
            "args": self.args,
            "return_type": self.return_type,
            "action_type": self.action_type
        }


if __name__ == "__main__":
    mutations = []
    for _ in mock_mutation["data"]["__schema"]["types"]:
        if _["name"]==mutation_type_name:
            mutations = _["fields"]

    for m in mutations:
        mutation = Mutation(m)
        pprint(mutation.to_dict())
        

