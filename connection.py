
import requests

URL = "http://neogeek.io:4000/graphql"

def query(query, url=URL):
    body = {
      "query": query 
    }

    res = requests.post(url, body)

    return res.text