import requests, functools, json

def send_request(url, query):

    body = { 
        "query": query
    }

    x = requests.post(
		url=url,
		json=body
	)
    return json.loads(x.text)


result = send_request("http://neogeek.io:4000/graphql", "")
print(result)