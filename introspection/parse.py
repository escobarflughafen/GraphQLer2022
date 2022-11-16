from graphql_types import mutation
from graphql_types import query
from graphql_types import interface
from graphql_types import enumeration
from graphql_types import input_object
from graphql_types import obj
import json
import yaml
import os
from connect import connect
import sys
sys.path.append(os.path.join(os.getcwd(), "graphql_types"))


class SchemaBuilder:
    def __init__(self, url=None, introspection_json=None):
        if introspection_json:
            self.raw_introspection_json = introspection_json
        elif url:
            self.raw_introspection_json = connect.fetch_introspection(url=url)
        else:
            raise Exception(
                "requires introspection source at parameter `url` or `introspection_json`")

        datatypes = build_datatype(self.raw_introspection_json)
        self.schema = {
            "objects": datatypes["objects"],
            "inputObjects": datatypes["input_objects"],
            "queries": build_query(self.raw_introspection_json),
            "mutations": build_mutation(self.raw_introspection_json),
            "enums": build_enumeration(self.raw_introspection_json),
            "interfaces": build_interface(self.raw_introspection_json),
        }
        self.instantiate()

    def instantiate(self):
        self.prepared_schema = {
            "objects": {
                k: obj.Object(k, schema_json=self.schema["objects"][k]) for k in self.schema["objects"]
            },
            "inputObjects": {
                k: input_object.InputObject(k, schema_json=self.schema["inputObjects"][k]) for k in self.schema["inputObjects"]
            },
            "queries": {
                k: query.Query(k, schema_json=self.schema["queries"][k]) for k in self.schema["queries"]
            },
            "mutations": {
                k: mutation.Mutation(k, schema_json=self.schema["mutations"][k]) for k in self.schema["mutations"]
            },
            "enums": {
                k: enumeration.Enum(k, schema_json=self.schema["enums"][k]) for k in self.schema["enums"]
            },
            "interfaces": {
                k: interface.Interface(k, schema_json=self.schema["interfaces"][k]) for k in self.schema["interfaces"]
            },
        }

    def dump(self, fp=None, path=None):
        json_literal = json.dumps(self.schema)

        if fp:
            json.dump(self.schema, fp)
        elif path:
            with open(path, "w") as f:
                json.dump(self.schema, f)
        else:
            print(json_literal, file=sys.stdout)

        return json_literal


# parse object type recursively
def of_type(typedef):
    if not typedef:
        return None
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

# parsing {query arguments || object fields} from intropsection json


def parse_args(args_raw, type_key="type"):
    args = None
    if args_raw:
        args = {}
        for arg_raw in args_raw:
            arg_name = arg_raw["name"]
            args[arg_name] = of_type(arg_raw[type_key])

    return args


def build_enumeration(introspection_json):
    enumerations = {}

    def is_user_defined_enum(raw_json):
        return raw_json["kind"] == "ENUM" and raw_json["name"][:2] != '__'

    type_data = introspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if is_user_defined_enum(d):
            enum_name = d["name"]
            enum = {
                "raw": d,
                "values": d["enumValues"]
            }
            enumerations[enum_name] = enum

    return enumerations


def build_interface(introspection_json):
    interfaces = {}

    def is_user_defined_interface(raw_json):
        return raw_json["kind"] == "INTERFACE" and raw_json["name"][:2] != '__'

    type_data = introspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if is_user_defined_interface(d):
            interface_name = d["name"]

            interface = {
                "raw": d,
                "kind": "INTERFACE",
                "fields": parse_args(d["fields"]),
                "interfaces": parse_args(d["interfaces"], type_key="ofType"),
                "possibleTypes": parse_args(d["possibleTypes"], type_key="ofType")
            }

            interfaces[interface_name] = interface

    return interfaces


def build_datatype(introspection_json):
    objects = {}
    input_objects = {}

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

    def is_user_defined_object_kind(typekind, typename):
        object_kinds = ['OBJECT', 'INPUT_OBJECT']
        object_name_filters = [query_type_name,
                               mutation_type_name, subscription_type_name]

        assertion = (typekind in object_kinds) and (
            typename[:2] != "__") and (typename not in object_name_filters)

        return assertion

    for d in type_data:
        typekind = d["kind"]
        typename = d["name"]
        if is_user_defined_object_kind(typekind, typename):
            object = {
                "raw": d,
                "kind": typekind,
            }

            if typekind == "OBJECT":
                objects[typename] = object
                # Filter out mutation & query & subscription & introspection system object.
                object["fields"] = parse_args(d["fields"])
                # TODO: 11-16'22
                # if the object is implementing a interface
                object["interfaces"] = parse_args(
                    d["interfaces"], type_key="ofType")

            elif typekind == "INPUT_OBJECT":
                input_objects[typename] = object
                object["fields"] = parse_args(d["inputFields"])

    return {
        "objects": objects,
        "input_objects": input_objects
    }


def build_query(introspection_json):
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
                queries[query_name]["args"] = parse_args(query_raw["args"])

    return queries


# predicates for determining mutation action type
# refer to https://www.apollographql.com/blog/graphql/basics/designing-graphql-mutations/

def build_mutation(introspection_json):
    def get_name(raw_introspection):
        return raw_introspection["name"]

    def get_return_type(raw_introspection):
        return raw_introspection["type"]

    def get_action_type(args):
        return ""

    mutations = {}
    raw_mutation_list = []

    mutation_type_name = introspection_json["data"]["__schema"]["mutationType"]["name"]

    for _ in introspection_json["data"]["__schema"]["types"]:
        if _["name"] == mutation_type_name:
            raw_mutation_list = _["fields"]

    for raw_mutation in raw_mutation_list:
        mutation = {
            # "name": get_name(raw_mutation), # unnecessary - use name as key
            "raw": raw_mutation,
            "args": parse_args(raw_mutation["args"]),
            "type": get_return_type(raw_mutation),
        }

        mutations[get_name(raw_mutation)] = mutation

    return mutations


def generate_grammar_file(path, objects, input_objects, queries, mutations, type="json"):
    if os.path.exists(path):
        raise Exception("File has already existed.")

    f = open(path, 'w')

    grammer = {
        "objects": objects,
        "inputObjects": input_objects,
        "queries": queries,
        "mutations": mutations
    }

    if type == "yaml":
        yaml.dump(grammer, f)
    elif type == "json":
        json.dump(grammer, f)

    f.close()


if __name__ == "__main__":
    print("parse.py")
