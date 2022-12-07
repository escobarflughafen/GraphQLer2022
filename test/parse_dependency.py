from networkx import DiGraph
import json


Schema = json.load(open('./grammar.json'))
input_objects = [_ for _ in Schema["DataTypes"] if _["kind"]=="INPUT_OBJECT"]
objects = [_ for _ in Schema["DataTypes"] if _["kind"] == "OBJECT"]
queries = Schema["Queries"]
mutations = Schema["Mutations"]

def get_ids(arg):
    ids = []
    if arg["type"]["name"] == "ID":
        ids.append(arg["name"])        
    elif arg["type"]["name"] == "INPUT_OBJECT":
        input_object = {}
        for iobj in input_objects:
            
    return ids
     

def parse():
    for mutation in mutations:
        for arg in mutation["args"]:
             
