import requests
import functools
import json
import yaml
from pprint import pprint

with open("./introspection.gql", "r") as igql:
    introspection_query = igql.read()


def fetch_introspection(url="http://neogeek.io:4000/graphql"):

    body = {
        "query": introspection_query
    }

    x = requests.post(
        url=url,
        json=body
    )

    return json.loads(x.text)
