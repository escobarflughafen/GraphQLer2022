from pprint import pprint
from queue import Queue
import json
# import networkx as nx
# import matplotlib.pyplot as plt

SCHEMAPATH = "./introspection/schema.json"

object_schema = json.load(open(SCHEMAPATH))["objects"]

object_queue = Queue()
object_sequence = []


def get_base_type_detail(type_def):
    '''
    Return object base type and name and non-null attribute.
    '''
    if type_def.get("ofType"):
        return get_base_type_detail(type_def["ofType"]) 
    else:
        if type_def.get("nonNull"): 
            return (type_def["kind"], type_def["name"], True)
        else:
            return (type_def["kind"], type_def["name"], False)


def get_consume(object_name):
    '''
    Take an object name
    Check what other object data types it consumes or depends on
    Return the list of objects it consumes (or empty list if none)
    ''' 
    consume_list = []
    params = object_schema[object_name]["fields"]
    for p_name, p_detail in params.items():
        base_type, ob_name, non_null = get_base_type_detail(p_detail)

        if base_type == "OBJECT" and non_null is True:
            consume_list.append(ob_name)
    return consume_list


def is_object_exist(object_list):
    '''
    Check if all the objects exist in the object sequence list at this point.
    If all exist return true, otherwise return false.
    '''
    for o in object_list:
        if o not in object_sequence:
            return False
    return True


# Add the name of all data type to the queue.
for dt in object_schema:
    object_queue.put(dt)

print("Initial queue")

while not object_queue.empty():
    ob = object_queue.get()
    print("current Object:")
    print(ob)

    consume_list = get_consume(ob)
    #print(consume_list)
    if not consume_list:
        object_sequence.append(ob)
    else:
        if is_object_exist(consume_list):
            object_sequence.append(ob)
        else:
            object_queue.put(ob)

print("Final sequence:")
for i in object_sequence:
    print(i)