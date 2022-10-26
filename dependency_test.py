import yaml
from pprint import pprint
import get_introspection
import introspection_query


# TODO: 1. REWRITE OUTPUT FORMAT. 

# TABLE:
'''
datapaye | type (query / mutation) | name | action

'''

data = get_introspection.parse(introspection_query.send_request())

# Get all query related to a specific data type 
def get_query_list(data_json, data_type):

    # Get lists of query name.
    query_name = ["messages", "getMessage"]   # TODO: work on the function to get all query name later.

    query_list = []
    for qn in query_name:
        for d in data_json:
            if d['name'] == qn:
                query_list.append(d)
        
    return query_list


def get_mutation_list(data_json, data_type):

    # Get lists of mutation name.
    mutation_name = ["createMessage", "updateMessage", "deleteMessage"] # TODO!!!! need to know the json format.

    mutation_list = []
    for mn in mutation_name:
            for d in data_json:
                if d['name'] == mn:
                    mutation_list.append(d)
    return mutation_list


def dependency_test():
    # 1. Get a random function from a mutation list => provide input object (maybe) => check the status code 200/400/any error.
    # 2. Call any query function => if success then the mutation is create.  

    return 


def build_query_string():
    query_string = ""

    '''
    query HeroNameAndFriends($episode: Episode) {
        hero(episode: $episode) {
            name
            friends {
            name
            }
        }
    }
    '''

    return query_string


def build_mutation_string():
    mutation_string = ""

    '''
    mutation
    '''

    return mutation_string


    

def get_mutation_create(data_type):
    return
    # 1. Loop though the list of mutation that related to specific data type.
     
    # Return JSON {"mutation_create:" [{"name": "", "produce:" "", "consume": ""}, {}, {}]}





data = get_query_list(data[1], "messages")
pprint(data)