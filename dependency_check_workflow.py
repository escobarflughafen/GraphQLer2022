from ast import Delete
from distutils.command.build import build
from random import random
from readline import append_history_file
from turtle import update
import requests, functools, json

from get_introspection_type import parse_data_type


datadb = {}
fuzz_int = [0,1,-1]
fuzz_string = ["wfr23","@$@UD@", " "]
fuzz_float = [12.123, 141.123124, .124]
fuzz_bool = ['false', 'true']
fuzz_id = ["14314", "qrqf2132", "@(Q@QQD"]

data_type_json = parse_data_type(connect.get_introspection(url="http://neogeek.io:4000/graphql"))

test_json = {"name": "getMessage", "produces": {"kind": "OBJECT", "name": "Message"}, "consumes": [{"name": "id", "type": {"kind": "NON_NULL", "name": null, "ofType": {"kind": "SCALAR", "name": "ID"}}}]}
test_object_list = {}

def fuzz_scalar(kind):
    if kind == "String":
        return random.choice(fuzz_string)
    elif kind == "Int":
        return random.choice(fuzz_int)
    elif kind == "Float":
        return random.choice(fuzz_float)
    elif kind == "Boolean":
        return random.choice(fuzz_bool)
    elif kind == "ID":
        return random.choice(fuzz_id)

def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type


def build_query_string(json_string):
    inner_json = {}
    query = "{" + json_string["name"] + "("
    for arg in json_string["consumes"]:
        data_type = get_type(arg)
        if data_type["kind"] == "SCALAR":
            inner_json[arg["name"]] = fuzz_scalar(data_type["name"])
        else:
            inner_json[arg["name"]] = build_object(search_object(data_type_json, data_type["name"]))
    query += json.dumps(inner_json) + ")\{\}\}"
    return query


def search_object(object_json, object_name):
    return object_json[object_name]


def build_object(object):
    inner_json = {}
    for arg in object["params"]:
        data_type = get_type(arg)
        if data_type["kind"] == "SCALAR":
            inner_json[arg["name"]] = fuzz_scalar(data_type["name"])
        else:
            inner_json[arg["name"]] = build_object(search_object(data_type_json, data_type["name"]))
    return inner_json




def send_request(url, query):

    body = { 
        "query": query
    }

    x = requests.post(
		url=url,
		json=body
	)
    return json.loads(x.text)

def dependency_check():
    for datatype in datatypes:
        first_mutation = get_mutation_with_input_type(datatype)
        queryString = build_query_string_input(first_mutation)
        first_result = send_request(url, queryString)
        datadb[datatype] = result.data

        second_query = get_query(datatype)
        queryString = build_query_string_with_data(second_query, datadb)
        second_result = send_request(url, queryString)

        thrid_query = get_mutation(datatype)
        queryString = build_query_string_with_data(thrid_query, datadb)
        thrid_result = send_request(url, queryString)

        forth_query = get_query(datatype)
        queryString = build_query_string_with_data(forth_query, datadb)
        forth_result = send_request(url, queryString)

        if second_result == 200 and forth_result == 200:
            writeback update
        elif second_result == 200 and forth_result == 400:
            writeback delete
            delete datadb[datatype]


