import requests, functools, json
import yaml
from pprint import pprint

def send_request():
    url = "http://neogeek.io:4000/graphql"


    body = {
        "query": """query IntrospectionQuery {
      __schema {

        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description

          locations
          args {
            ...InputValue
          }
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description

      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }

    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue


    }

    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }

        """
    }


    x = requests.post(
        url=url,
        json=body
    )

    return json.loads(x.text)

def recursive_oftype(data):
  if(data["ofType"] == None):
    return {"kind" : data["kind"], "name" : data["name"]}
  else:
    return {"kind" : data["kind"], "name" : data["name"], "ofType" : recursive_oftype(data["ofType"])}


def parse(inspection_json):
    input_object_list = []
    object_list = []
    scalar_list = []
    enum_list = []
    query_list = []
    mutation_list = []

    query_type_name = inspection_json["data"]["__schema"]["queryType"]["name"]
    mutation_type_name = inspection_json["data"]["__schema"]["mutationType"]["name"]
    type_data = inspection_json["data"]["__schema"]["types"]

    for d in type_data:
        if d["kind"] == "INPUT_OBJECT":
            object = {}
            object["name"] = d["name"]
            object["inputFields"] = d["inputFields"]
            input_object_list.append(object)
        elif d["kind"] == "OBJECT":
            if d["name"] == query_type_name:
                for f in d["fields"]:
                    object = {}
                    object["name"] = f["name"]
                    types = {}
                    types = recursive_oftype(f["type"])

                    object["produces"] = types

                    object["consumes"] = []

                    for a in f["args"]:
                        arg = {}
                        arg["name"] = a["name"]
                        types = {}
                        types = recursive_oftype(f["type"])
                        arg["type"] = types

                        object["consumes"].append(arg)

                    query_list.append(object)
                    '''
            elif d["name"] == mutation_type_name:
                for f in d["fields"]:
                    object = {}
                    object["name"] = f["name"]
                    object["type"] = f["type"]
                    object["args"] = []

                    for a in f["args"]:
                        arg = {}
                        arg["name"] = a["name"]
                        object["args"].append(arg)

                    mutation_list.append(object)
            else:
                object = {}
                for f in d["fields"]:
                    object["name"] = f["name"]
                    object["type"] = f["type"]["kind"]
                object_list.append(object)
                '''
        elif d["kind"] == "SCALAR":
            scalar_list.append(d)
        elif d["kind"] == "ENUM":
            enum_list.append(d)

    return input_object_list, object_list, scalar_list, enum_list, query_list, mutation_list



data = parse(send_request())
pprint(data)


test = yaml.dump(data)
print(test)









