import yaml
from pprint import pprint

from other.introspection_query import *


def get_type(inspection_param_json):
	if inspection_param_json["ofType"] is None:
		return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"] }
	else:
		return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"], "ofType" : get_type(inspection_param_json["ofType"])}


# Parse introspection to generate a YAML grammar file.
def parse(inspection_json):
	object_list = []
	query_list = []
	mutation_list = []

	scalar_list = []
	enum_list = []

	# Get query type name
	query_type_name = None if inspection_json["data"]["__schema"]["queryType"] is None else inspection_json["data"]["__schema"]["queryType"]["name"]

	# Get mutation type name
	mutation_type_name = None if inspection_json["data"]["__schema"]["mutationType"] is None else inspection_json["data"]["__schema"]["mutationType"]["name"]

	# TODO: Get subscription type name
	subscription_type_name = None if inspection_json["data"]["__schema"]["subscriptionType"] is None else inspection_json["data"]["__schema"]["subscriptionType"]["name"]

	type_data = inspection_json["data"]["__schema"]["types"]

	for d in type_data:
		# INPUT_OBJECT
		if d["kind"] == "INPUT_OBJECT":
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

		elif d["kind"] == "OBJECT":
			# QUERY
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
			
			# MUTATION
			elif d["name"] == mutation_type_name:
				'''
				elif d["name"] == mutation_type_name:
				for f in d["fields"]:
					object = {}
					object["name"] = f["name"]
					object["type"] = f["type"]
					object["args"] = []

					for a in f["args"]:
						arg = {}
						arg["name"] = a["name"]
						object["args"].append(arg)

					mutation_list.append(object)
			
				'''

			# DATA_TYPE: Filter out multation & query & subscription & introspection system object.
			elif d["name"] != subscription_type_name and d["name"][:2] != "__":
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

		elif d["kind"] == "SCALAR":
			scalar_list.append(d)
		elif d["kind"] == "ENUM":
			enum_list.append(d)

	return object_list, query_list, mutation_list, scalar_list, enum_list


data = parse(send_request())

# TEST
# print(data[1])

file = open("grammar.yml", "w")

yaml.dump({"DataTypes": data[0], "Queries": data[1], "Mutations": data[2]}, file)

# TEST
test = yaml.dump(data[2])
# print(test)