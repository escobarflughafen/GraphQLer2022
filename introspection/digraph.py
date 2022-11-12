import networkx as nx
import json

objects = json.load(open(
    './grammar_2022-11-09-16-18-57.json'
))["DataTypes"]

def get_object_graph(objects):
    G = nx.DiGraph()

    for object in objects:
        if objects[object]["kind"] == "OBJECT":
            G.add_node(object, **objects[object])

    for n_1 in G:
        for n_2 in G:
            n_1_data = G.nodes[n_1]
            n_2_data = G.nodes[n_2]
            if (n_1 != n_2) and (n_1_data["kind"] == "OBJECT" and n_2_data["kind"] == "OBJECT"):
                params = n_1_data["params"]
                for param in params:
                    if params[param]["kind"] == "OBJECT" and params[param]["name"] == n_2:
                        G.add_edge(n_1, n_2)
    
    return G

G = get_object_graph(objects)

def get_input_object_graph(object_graph, input_objects):
    G = nx.Graph.copy(object_graph)

    for input_object_key in input_objects:
        input_object = input_objects[input_object_key]    
        G.add_node(input_object_key, **input_object)
        

    return G

for e in G.edges:
    print(e)