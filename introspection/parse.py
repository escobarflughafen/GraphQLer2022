import requests
import functools
import json
import yaml
from pprint import pprint
import connect
import pathlib
import os


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


def parse_data_type(inspection_json):

    object_list = []

    # Get query type name
    query_type_name = inspection_json["data"]["__schema"]["queryType"]["name"]

    # Get mutation type name
    mutation_type_name = inspection_json["data"]["__schema"]["mutationType"]["name"]

    # Get subscription type name
    # subscription_type_name = inspection_json["data"]["__schema"]["subscriptionType"]["name"]

    type_data = inspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if d["kind"] == "OBJECT":
            # Filter out multation & query & subscription & introspection system object.
            if d["name"] != query_type_name and d["name"] != mutation_type_name and d["name"][:2] != "__":
                object = {}
                object_name = d["name"]
                object_params = {}
                object_params["params"] = {}

                for f in d["fields"]:
                    param_name = f["name"]
                    param_type = {}
                    param_type = get_type(f["type"])

                    # Add to the parameter list.
                    object_params["params"][param_name] = param_type

                object[object_name] = object_params
                object_list.append(object)

        elif d["kind"] == "INPUT_OBJECT":
            object = {}
            object_name = d["name"]
            object_params = {}
            object_params["params"] = {}

            for f in d["inputFields"]:
                param_name = f["name"]
                param_type = {}
                param_type = get_type(f["type"])

                # Add to the parameter list.
                object_params["params"][param_name] = param_type

            object[object_name] = object_params
            object_list.append(object)

    return object_list


def parse_query(introspection_json):
    query_list = []

    # Get query type name
    query_type_name = introspection_json["data"]["__schema"]["queryType"]["name"]

    type_data = introspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if d["kind"] == "OBJECT":
            if d["name"] == query_type_name:
                for f in d["fields"]:
                    object = {}
                    object["name"] = f["name"]
                    types = {}
                    types = get_type(f["type"])

                    object["produces"] = types

                    object["consumes"] = []

                    for a in f["args"]:
                        arg = {}
                        arg["name"] = a["name"]
                        types = {}
                        types = get_type(f["type"])
                        arg["type"] = types

                        object["consumes"].append(arg)

                    query_list.append(object)

    return query_list


def get_name(raw_introspection):
    return raw_introspection["name"]


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


def parse_mutation(introspection_json):
    mutation_list = []
    raw_mutation_list = []

    mutation_type_name = introspection_json["data"]["__schema"]["mutationType"]["name"]

    for _ in introspection_json["data"]["__schema"]["types"]:
        if _["name"] == mutation_type_name:
            raw_mutation_list = _["fields"]

    for raw_mutation in raw_mutation_list:
        mutation = {
            "name": get_name(raw_mutation),
            "args": get_args(raw_mutation),
            "return_type": get_return_type(raw_mutation)
        }

        mutation["action_type"] = get_action_type(mutation["args"])

        mutation_list.append(mutation)

    return mutation_list


def parse_dependency(data_types, queries, mutations):
    counter = 1
    type_action_lookup = {
      
    }
    
    while counter > 0:
        for i in range(len(mutations)):
          if mutations[i]["action_type"] == "CREATE":
            
              

def generate_grammar_file(path, data_types, queries, mutations):
    if os.path.exists(path):
        raise Exception("File has already existed.")

    f = open(path, 'w')

    grammer = {
        "DataTypes": data_types,
        "Queries": queries,
        "Mutations": mutations
    }

    yaml.dump(grammer, f)
    f.close()


if __name__ == "__main__":
    introspection_json = connect.get_introspection(
        url="http://neogeek.io:4000/graphql")

    object_type_list = parse_data_type(introspection_json)
    query_list = parse_query(introspection_json)
    mutation_list = parse_mutation(introspection_json)

    generate_grammar_file(
        './grammer.yaml', object_type_list, query_list, mutation_list)

    print(json.dumps(object_type_list, indent=2))
    print(json.dumps(query_list, indent=2))
    print(json.dumps(mutation_list, indent=2))

    '''
    yaml.dump(object_type_list, open("./object_type_list.yml", "w"))
    yaml.dump(query_list, open("./query_list.yml", "w"))
    yaml.dump(mutation_list, open("./mutation_list.yml", "w"))
    '''
