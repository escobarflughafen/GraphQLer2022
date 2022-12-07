import networkx as nx
import matplotlib.pyplot as plt
from introspection import parse
import json



def is_dependent(obj1, obj3):
    pass

def build_object_graph(objects):
    G = nx.DiGraph()
    

def get_object_graph(objects):
    G = nx.DiGraph()

    for object in objects:
        if objects[object]["kind"] == "OBJECT":
            G.add_node(object, **objects[object])
    
    def is_dependent_on(param, objname):
        if param["kind"] == "LIST":
            return is_dependent_on(param["ofType"], objname)

        return param["kind"] == "OBJECT" and param["name"] == objname

    for n_1 in G:
        for n_2 in G:
            n_1_data = G.nodes[n_1]
            n_2_data = G.nodes[n_2]
            if (n_1 != n_2) and (n_1_data["kind"] == "OBJECT" and n_2_data["kind"] == "OBJECT"):
                params = n_1_data["fields"]
                for param in params:
                    if is_dependent_on(params[param], n_2):
                        G.add_edge(n_1, n_2)
    
    return G


def get_input_object_graph(object_graph, input_objects):
    G = nx.Graph.copy(object_graph)

    for input_object_key in input_objects:
        input_object = input_objects[input_object_key]    
        G.add_node(input_object_key, **input_object)
        
    return G




#if __name__ == '__main__':
def test():
    '''
    objects = json.load(open(
        './shopify_schema.json'
    ))["objects"]
    '''
    
    schema = parse.SchemaBuilder(url="http://neogeek.io:4001/graphql")

    G = get_object_graph(schema.schema["objects"])
    sequence = list(reversed(list(nx.topological_sort(G))))
    print(sequence)
    