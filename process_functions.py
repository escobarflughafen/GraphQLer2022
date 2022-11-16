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
f = open("schema.json", "r")
objects = json.load(f)


def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type




def link_scalar_with_dataType(objects):
    list = {}
    for key, value in objects.items():
        for kkey, vvalue in value["fields"].items():
            list[kkey] = {}
            list[kkey]["kind"] = value["kind"]
            list[kkey]["name"] = key
    return list

def link_inputDatatype_with_dataType(objects):
    list = {}
    for key, value in objects.items():
        for kkey, vvalue in value["fields"].items():
            list[kkey] = {}
            list[kkey]["kind"] = value["kind"]
            list[kkey]["name"] = key
    return list



def get_scalar_with_datatype(name):
    test = link_scalar_with_dataType(objects["objects"])
    test2 = link_inputDatatype_with_dataType(objects["inputObjects"])
    list = {}
    test.update(test2)
    if test.get(name) != None:
        return test[name]["name"]
    else:
        return None



def link_function_with_datatype(list, functionName, functionObject):
    output = functionObject["type"]
    data_type = get_type(output)
    if data_type["kind"] == "OBJECT":
        list[functionName] = {}
        list[functionName]["rawdata"] = functionObject["raw"]
        list[functionName]["inputDatatype"] = []
        for argkey, argobject in functionObject["args"].items():
            list[functionName]["inputDatatype"].append(get_scalar_with_datatype(argkey))
        list[functionName]["outputDataType"] = output["name"]

    elif data_type == "SCALAR":
        list[functionName] = {}
        list[functionName]["rawdata"] = functionObject["raw"]
        list[functionName]["inputDatatype"] = []
        list[functionName]["outputDataType"] = arg["name"]

    elif data_type == "INTERFACE":
        pass
    elif data_type == "UNION":
        pass

    elif data_type == "ENUM":
        pass

    elif data_type == "INPUT_OBJECT":
        pass

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
                

for key, value in objects["mutations"].items():
    link_function_with_datatype(list, key, value)
for object in objects["Queries"]:
    link_function_with_datatype(list, object)
print(list)

