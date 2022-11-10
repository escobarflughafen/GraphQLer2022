from random import random
import requests, json
import introspection.connect as connect
import networkx
import introspection.parse as parse
import random
import re


def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type


list = {}
f = open("grammer.json", "r")
objects = json.load(f)

def link_function_with_datatype(list, object):
    scalarOnly = True
    arg = object["return_type"]
    data_type = arg["kind"]
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
                
for object in objects["Mutations"]:
    link_function_with_datatype(list, object)
for object in objects["Queries"]:
    link_function_with_datatype(list, object)
print(list)

