import yaml

from other.introspection_query import *


def parse_data_type(inspection_json):

	object_list = []

	# Get query type name
	query_type_name = inspection_json["data"]["__schema"]["queryType"]["name"]

	# Get mutation type name
	mutation_type_name = inspection_json["data"]["__schema"]["mutationType"]["name"]

	# Get subscription type name
	subscription_type_name = inspection_json["data"]["__schema"]["subscriptionType"]["name"]

	type_data = inspection_json["data"]["__schema"]["types"]

	for d in type_data:
		if d["kind"] == "OBJECT":
			# Filter out multation & query & subscription & introspection system object.
			if d["name"] != query_type_name and d["name"] != mutation_type_name and d["name"] != subscription_type_name and d["name"][:2] != "__":
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


def get_type(inspection_param_json):
	if inspection_param_json["ofType"] is None:
		return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"] }
	else:
		return { "kind" : inspection_param_json["kind"], "name" : inspection_param_json["name"], "ofType" : get_type(inspection_param_json["ofType"])}



data = parse_data_type(send_request())
print(data)

ymal = yaml.dump(data)
print(ymal)

# Output to a YAML file.
file = open("type.yml", "w")
yaml.dump_all(data, file)