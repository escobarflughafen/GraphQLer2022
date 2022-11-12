import json
import yaml
from pprint import pprint
import connect
import os
from datetime import datetime

# parse ofType field recursively
def of_type(typedef):
    if "ofType" in typedef:
        if typedef["ofType"] == None:
            return {
                "kind": typedef["kind"],
                "name": typedef["name"]
            }
        else:
            # flatten non-null wrapper
            kind = typedef["kind"]
            if kind == "NON_NULL":
                _type = of_type(typedef["ofType"])
                return {
                    **_type,
                    "nonNull": True
                }
            else:
                return {
                    "kind": kind,
                    "name": typedef["name"],
                    "ofType": of_type(typedef["ofType"]),
                }
    else:
        return {
            "kind": typedef["kind"],
            "name": typedef["name"]
        }


def parse_data_type(introspection_json):
    objects = {}

    # Get query type name
    query_type_name = introspection_json["data"]["__schema"]["queryType"]["name"]

    # Get mutation type name
    try:
        mutation_type_name = introspection_json["data"]["__schema"]["mutationType"]["name"]
    except Exception:
        mutation_type_name = ""

    # Get subscription type name
    try:
        subscription_type_name = introspection_json["data"]["__schema"]["subscriptionType"]["name"]
    except Exception:
        subscription_type_name = ""

    type_data = introspection_json["data"]["__schema"]["types"]

    def is_object_kind(typekind):
        filters = ["SCALAR", query_type_name,
                   mutation_type_name, subscription_type_name]
        
        assertion = (typekind not in filters) and typekind[:2] != "__"
        # print(typekind, assertion)

        return assertion


    for d in type_data:
        if is_object_kind(d["kind"]):
            typename = d["name"]
            objects[typename] = {}
            objects[typename]["kind"] = d["kind"]
            objects[typename]["raw"] = d
            if d["kind"] == "OBJECT":
                # Filter out multation & query & subscription & introspection system object.
                objects[typename]["fields"] = {}

                for f in d["fields"]:
                    param_name = f["name"]
                    param_type = {}
                    param_type = of_type(f["type"])

                    # Add to the parameter list.
                    objects[typename]["fields"][param_name] = param_type

            elif d["kind"] == "INPUT_OBJECT":
                objects[typename]["fields"] = {}

                for f in d["inputFields"]:
                    param_name = f["name"]
                    param_type = {}
                    param_type = of_type(f["type"])

                    # Add to the parameter list.
                    objects[typename]["fields"][param_name] = param_type

    return objects


def parse_query(introspection_json):
    queries = {}

    # Get query type name
    query_type_name = introspection_json["data"]["__schema"]["queryType"]["name"]
    type_data = introspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if d["kind"] == "OBJECT" and d["name"] == query_type_name:
            for query_raw in d["fields"]:
                # parsing query properties
                query_name = query_raw["name"]
                queries[query_name] = {}

                queries[query_name]["raw"] = query_raw
                queries[query_name]["type"] = of_type(query_raw["type"])
                queries[query_name]["args"] = {}
                args = queries[query_name]["args"]

                # parsing query arguments
                for arg_raw in query_raw["args"]:
                    arg_name = arg_raw["name"]
                    args[arg_name] = {}
                    args[arg_name]["type"] = of_type(arg_raw["type"])

    return queries


def get_name(raw_introspection):
    return raw_introspection["name"]


def get_args(raw_introspection):
    args = {}
    raw_args = raw_introspection["args"]
    for arg in raw_args:
        obj = {}
        # obj["name"] = arg["name"]
        obj["type"] = of_type(arg["type"])
        obj["defaultValue"] = arg["defaultValue"]

        args[arg["name"]] = obj

    return args

def get_return_type(raw_introspection):
    return raw_introspection["type"]

# predicates for determining mutation action type

# refer to https://www.apollographql.com/blog/graphql/basics/designing-graphql-mutations/

def get_action_type(args):
    has_input_field = False
    has_id_field = False
    for arg in args:
        if args[arg]["type"]["kind"] == "SCALAR" and args[arg]["type"]["name"] == "ID":
            has_id_field = True

        elif args[arg]["type"]["kind"] == "INPUT_OBJECT":
            has_input_field = True

    if has_input_field and has_id_field:
        return "UPDATE"

    if has_input_field and not has_id_field:
        return "CREATE"

    if not has_input_field and has_id_field:
        return "DELETE"

    return "OTHER"


'''
def get_all_required_ids_in_args(mutation, datatypes):
    input_objects = [
        ""    
    ]
    ids = []
    
    def traverse(args):
        for arg in args:
            if arg["type"]["kind"] == "SCALAR" and arg["type"]["name"] == "ID" and arg["type"]["nonNull"]:
                ids.append(arg["name"])
            elif arg[""]
'''


def parse_mutation(introspection_json):
    mutations = {}
    raw_mutation_list = []

    mutation_type_name = introspection_json["data"]["__schema"]["mutationType"]["name"]

    for _ in introspection_json["data"]["__schema"]["types"]:
        if _["name"] == mutation_type_name:
            raw_mutation_list = _["fields"]

    for raw_mutation in raw_mutation_list:
        mutation = {
            # "name": get_name(raw_mutation), # unnecessary - use name as key
            "args": get_args(raw_mutation),
            "return_type": get_return_type(raw_mutation)
        }

        mutation["action_type"] = get_action_type(mutation["args"])
        mutations[get_name(raw_mutation)]=mutation

    return mutations


def parse_dependency(datatypes, queries, mutations):
    counter = 1
    input_objects = [
        datatype for datatype in datatypes if datatype["kind"] == "INPUT_OBJECT"
    ]

    parsed_mutations = []

    while counter > 0:
        for mutation in mutations:
            pass
            '''
            if mutation["action_type"] == 'CREATE':
                for arg in mutation["args"]:
                    
                

            elif mutation["action_type"] == 'DELETE':

            elif mutation["action_type"] == 'UPDATE':
            '''

        '''
        for i in range(len(mutations)):
            if mutations[i]["action_type"] == "CREATE":
                for arg in mutations[i]["args"]
        '''

    return parsed_mutations


def generate_grammar_file(path, data_types, queries, mutations, type="yaml"):
    if os.path.exists(path):
        raise Exception("File has already existed.")

    f = open(path, 'w')

    grammer = {
        "DataTypes": data_types,
        "Queries": queries,
        "Mutations": mutations
    }

    if type == "yaml":
        yaml.dump(grammer, f)
    else:
        json.dump(grammer, f)

    f.close()


if __name__ == "__main__":
    introspection_json = connect.fetch_introspection(
        url="http://neogeek.io:4000/graphql")

    #json_f = open("./introspection/examples/shopify_introspection.json")
    #introspection_json = json.load(json_f)
    # json_f.close()

    datatypes = parse_data_type(introspection_json)
    queries = parse_query(introspection_json)
    mutations = parse_mutation(introspection_json)

    generate_grammar_file(
        './grammar_{}.json'.format(datetime
                                   .now()
                                   .strftime("%Y-%m-%d-%H-%M-%S")),
        datatypes, queries, mutations, type="json")

    #print(json.dumps(datatypes, indent=2))
    #print(json.dumps(queries, indent=2))
    #print(json.dumps(mutations, indent=2))

    '''
    yaml.dump(object_type_list, open("./object_type_list.yml", "w"))
    yaml.dump(query_list, open("./query_list.yml", "w"))
    yaml.dump(mutation_list, open("./mutation_list.yml", "w"))
    '''
