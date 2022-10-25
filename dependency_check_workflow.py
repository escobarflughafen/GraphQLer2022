from ast import Delete
from turtle import update
import requests, functools, json


datadb = {}
fuzz_int = [0,1,-1]
fuzz_string = ["wfr23","@$@UD@", " "]
fuzz_bool = ['false', 'true']
fuzz_id = ["14314", "qrqf2132", "@(Q@QQD"]


def build_query_string_input(config):
    config["consumes"]


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


def build_query_string_input(query_json):
    query_json["name"]
    query_json["consumes"]
    query_json["produces"]
