import networkx as nx
import json

objects = json.loads(
    """
        {
            "MessageInput": {
                "params": {
                    "content": {
                        "kind": "SCALAR",
                        "name": "String"
                    },
                    "authorId": {
                        "kind": "SCALAR",
                        "name": "String"
                    }
                },
                "kind": "INPUT_OBJECT"
            },
            "AuthorInput": {
                "params": {
                    "firstName": {
                        "kind": "SCALAR",
                        "name": "String"
                    },
                    "lastName": {
                        "kind": "SCALAR",
                        "name": "String"
                    }
                },
                "kind": "INPUT_OBJECT"
            },
            "Message": {
                "params": {
                    "id": {
                        "kind": "SCALAR",
                        "name": "ID",
                        "nonNull": true
                    },
                    "content": {
                        "kind": "SCALAR",
                        "name": "String"
                    },
                    "author": {
                        "kind": "OBJECT",
                        "name": "Author"
                    }
                },
                "kind": "OBJECT"
            },
            "Author": {
                "params": {
                    "id": {
                        "kind": "SCALAR",
                        "name": "ID",
                        "nonNull": true
                    },
                    "firstName": {
                        "kind": "SCALAR",
                        "name": "String"
                    },
                    "lastName": {
                        "kind": "SCALAR",
                        "name": "String"
                    }
                },
                "kind": "OBJECT"
            }
        }
    """
)

G = nx.DiGraph()

for object in objects:
    if objects[object]["kind"] == "OBJECT":
        print(object)
        G.add_node(object, **objects[object])
    
print(G.nodes(data=True))


for n_1 in G:
    for n_2 in G:
        n_1_data = G.nodes[n_1]
        n_2_data = G.nodes[n_2]
        if (n_1 != n_2) and (n_1_data["kind"] == "OBJECT" and n_2_data["kind"] == "OBJECT"):
            params = n_1_data["params"]
            for param in params:
                if params[param]["kind"] == "OBJECT" and params[param]["name"] == n_2:
                    G.add_edge(n_1, n_2)

                    
print(G.edges)




