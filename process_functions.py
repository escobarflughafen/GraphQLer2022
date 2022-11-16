from random import random
import requests, json
import introspection.connect as connect
import networkx
import introspection.parse as parse
import random
import re



class FunctionDict:
    

    def __init__(self):
        self.name = {}
        self.rawdata = object
        self.inputDataType = {}
        self.outputDataType = {}
    
    def setInputDataType(self):
        return

    def getInputDataType(self):
        return

    def setOutPutDataType(self):
        return

    def getOutPutDataType(self):
        return

    def getRawdata(self):
        return self.rawdata



list = {}
f = open("schema2.json", "r")
objects = json.load(f)


def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type




def link_objects_with_data_type(objects):
    list = {}
    for object_name, object_body in objects.items():
        for field_name, field_value in object_body["fields"].items():
            list[field_name] = {}
            list[field_name]["kind"] = object_body["kind"]
            list[field_name]["name"] = object_name
    return list

def get_scalar_with_datatype(name):
    test = link_objects_with_data_type(objects["objects"])
    test2 = link_objects_with_data_type(objects["inputObjects"])
    list = {}
    test.update(test2)
    if test.get(name) != None:
        return test[name]["name"]
    else:
        return None


def search_related_object(objects, id_name, object_name):
    result = None
    for arg_name, arg_body in objects[object_name]["fields"].items():
        if arg_body["kind"] == "SCALAR" and arg_body["name"] == "ID":
            result = object_name
            return result
        elif arg_body["kind"] == "OBJECT":
            result = search_related_object(objects, id_name, arg_body["name"])
            if result != None:
                return result

    return result



def link_functions_with_datatype(objects):
    list = {}
    function_objects = objects["mutations"]

    for function_name, function_body in function_objects.items():
        input_args = function_body["args"]
        output = function_body["type"]
        output_data_type = get_type(output)

        if output_data_type["kind"] == "OBJECT":
            list[function_name] = {}
            list[function_name]["rawdata"] = function_body
            list[function_name]["inputDatatype"] = {}
            list[function_name]["outputDatatype"] = output_data_type
            for arg_name, arg_body in function_body["args"].items():
                arg_data_type = get_type(arg_body)
                if arg_data_type["kind"] == "SCALAR" and arg_data_type["name"] == "ID":
                    # search for output datatype
                    list[function_name]["inputDatatype"][arg_name] = search_related_object(objects["objects"], arg_name, output_data_type["name"])
                elif arg_data_type["kind"] == "SCALAR" or arg_data_type["kind"] == "ENUM":
                    list[function_name]["inputDatatype"][arg_name] = get_scalar_with_datatype(arg_name)
                elif arg_data_type["kind"] == "INPUT_OBJECT":
                    list[function_name]["inputDatatype"][arg_name] = arg_data_type

        elif output_data_type == "SCALAR":
            list[function_name] = {}
            list[function_name]["rawdata"] = function_object["raw"]
            list[function_name]["inputDatatype"] = []
            list[function_name]["outputDataType"] = arg["name"]

        elif output_data_type == "INTERFACE":
            pass
        elif output_data_type == "UNION":
            pass

        elif output_data_type == "ENUM":
            pass

        elif output_data_type == "INPUT_OBJECT":
            pass

    return list


def link_function_with_datatype_input(list, object):
    scalarOnly = True
    for arg in object["args"]:
        data_type = get_type(arg["type"])
        if data_type == "OBJECT":
            if list.get(arg["name"]) != None:
                list[arg["name"]].append(object)
            else:
                list[arg["name"]] = []
                list[arg["name"]].append(object)
            scalarOnly = False
    if scalarOnly:
        if list.get("scalarOnly") != None:
            list["scalarOnly"].append(object)
        else:
            list["scalarOnly"] = []
            list["scalarOnly"].append(object)

    return
                

test5 = link_functions_with_datatype(objects)
for object in objects["Queries"]:
    link_function_with_datatype(list, object)
print(list)

