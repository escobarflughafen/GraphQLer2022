from random import random
import requests, json
import introspection.connect as connect
import introspection.parse as parse
import random
import re


datadb = {}
fuzz_int = [0,1,-1]
fuzz_string = ["wfr23","@$@UD@", "7h "]
fuzz_float = [12.123, 141.123124, .124]
fuzz_bool = ['false', 'true']
fuzz_id = ["14314", "qrqf2132", "@(Q@QQD"]

data_type_json = parse.parse_data_type(connect.get_introspection(url="http://neogeek.io:4000/graphql"))

test_json = {'name': 'getMessage', 'produces': {'kind': 'OBJECT', 'name': 'Message'}, 'consumes': [{'name': 'id', 'type': {'kind': 'SCALAR', 'name': 'ID', 'nonNull': True}}]}
test_json2 = {'name': 'createMessage', 'args': [{'name': 'input', 'type': {'kind': 'INPUT_OBJECT', 'name': 'MessageInput'}, 'defaultValue': None}], 'return_type': {'kind': 'OBJECT', 'name': 'Message', 'ofType': None}, 'action_type': 'CREATE'}

# To generate a pre-defined random value to the input
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

# To get the last type which usually indicates the real basic type
def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type

# Build the query string based on the given schema of a Query (in JSON)
# If there's no database input, it will randomly generate the value
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

# Build the mutation string based on the given schema of a Mutation (in JSON)
# If there's no database input, it will randomly generate the value
def build_mutation_string(json_string, dbdata = {}):
    inner_json = {}
    query = "mutation {" + json_string["name"] + "("
    for arg in json_string["args"]:
        data_type = get_type(arg["type"])
        if data_type["kind"] == "SCALAR":
            inner_json[arg["name"]] = dbdata[arg["name"]] if dbdata.get(arg["name"]) != None else fuzz_scalar(data_type["name"])
        else:
            inner_json[arg["name"]] = build_object(search_object(data_type_json, data_type["name"]))
    # Remove the double quote for key but not the value (since GraphQL query did not like it)
    query += re.sub(r'(?<!: )"(\S*?)"', '\\1' ,json.dumps(inner_json)[1:-1]) + ")"
    
    data_type = get_type(json_string["return_type"])
    if data_type["kind"] == "SCALAR":
        query += data_type["name"] + " " # it seems no SCALAR will exists in the first layer so this line will never run, anyways this line of code is broken
    else:
        query += build_return_object(search_object(data_type_json, data_type["name"]))

    query += "}"
    
    return query

# take the object name and search from the Datatype area, return the schema of the Datatype (in JSON)
def search_object(object_json, object_name):
    for item in object_json:
        if item.get(object_name) != None:
            print(item.get(object_name))
            return item[object_name]


# Build the object JSON structure
def build_object(object):
    inner_json = {}
    for arg in object["params"].items():
        data_type = get_type(arg[1])
        if data_type["kind"] == "SCALAR":
            inner_json[arg[0]] = fuzz_scalar(data_type["name"])
        else:
            inner_json[arg[0]] = build_object(search_object(data_type_json, data_type["name"]))
    return inner_json

# To build the return area of the query/mutation string
def build_return_object(object):
    inner_string = " { "
    for arg in object["params"].items():
        data_type = get_type(arg[1])
        if data_type["kind"] == "SCALAR":
            inner_string += arg[0] + " "
        else:
            inner_string += arg[0] + build_return_object(search_object(data_type_json, data_type["name"]))
    inner_string += " } "
    return inner_string
    




def send_request(url, query):

    body = { 
        "query": query
    }

    x = requests.post(
		url=url,
		json=body
	)
    return json.loads(x.text)



if __name__ == "__main__":
    test = build_query_string(test_json)
    test2 = build_mutation_string(test_json2)
    print(test)
    url="http://neogeek.io:4000/graphql"
    result = send_request(url, test)
    result2 = send_request(url, test2)
    print(result)
    print(result2)


def get_query():
    return

def get_mutation():
    return

def get_mutation_with_input_type(datatype):
    return



def dependency_check(datatypes):
    for datatype in datatypes:
        first_mutation = get_mutation_with_input_type(datatype)
        queryString = build_query_string(first_mutation)
        first_result = send_request(url, queryString)
        datadb[datatype] = result.data

        second_query = get_query(datatype)
        queryString = build_query_string(second_query, datadb)
        second_result = send_request(url, queryString)

        thrid_query = get_mutation(datatype)
        queryString = build_query_string(thrid_query, datadb)
        thrid_result = send_request(url, queryString)

        forth_query = get_query(datatype)
        queryString = build_query_string(forth_query, datadb)
        forth_result = send_request(url, queryString)

        if second_result.get("errors") == None and forth_result.get("errors") != None:
            a=a# the resource has been deleted, write back delete
        elif second_result.get("errors") == None and forth_result.get("errors") == None:
            a=a# the resource is not deleted, probably update


