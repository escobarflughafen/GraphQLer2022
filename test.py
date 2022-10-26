from cgi import test
from imghdr import tests
from introspection_query import * 
import yaml
import json

url = "http://neogeek.io:4000/graphql"

def get_type(inspection_param_json):
    if inspection_param_json["ofType"] is None:
        return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"] }
    else:
        return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"], "ofType" : get_type(inspection_param_json["ofType"])}

def parse_query(inspection_json):

    query_list = []

	# Get query type name
    query_type_name = inspection_json["data"]["__schema"]["queryType"]["name"]

    type_data = inspection_json["data"]["__schema"]["types"]

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
                        types = get_type(a["type"])
                        arg["type"] = types

                        object["consumes"].append(arg)

                    query_list.append(object)

    return query_list



data = parse_query(send_request(url))
print(data)

teststring = json.dumps(data[2])
print(teststring)


