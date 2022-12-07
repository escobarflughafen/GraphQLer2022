import random
import json
from pprint import pprint

class Cache:
    def __init__(self, schema):
        self.schema = schema

        self.cache = {
            "id": {
                objname: [] for objname in schema["objects"]
            },
            "input_objects": {
                in_obj_name: [] for in_obj_name in schema["inputObjects"]
            },
            "unique_objects": {
                objname: {} for objname in schema["objects"]
            },
            "objects": {
                objname: [] for objname in schema["objects"]
            }
        }

    def get_random_id_by_type(self, object_name, non_used_only=False, max_attempts=1000):
        '''
            randomly return a id for a certain object type in the cache
        '''
        id_cache = self.cache["id"][object_name]

        index = random.randint(0, len(id_cache))
        cached_object = id_cache[random.randint(0, len(id_cache))]

        if non_used_only:
            attempt_counter = 1
            while cached_object["status"] == "used" and attempt_counter < max_attempts:
                cached_object = id_cache[random.randint(0, len(id_cache)-1)]
                attempt_counter += 1

        cached_object["status"] = "used"

        return cached_object["value"]

    def get_object_by_id(self, object_name, id):
        '''
            return a object by id of certain object type
        '''
        unique_object_cache = self.cache["unique_objects"]

        return unique_object_cache[object_name][id]

    def get_random_object(self, object_name, non_used_only=False, max_attempts=1000):
        '''
            return a random object by object name
        '''
        object_cache = self.cache["objects"][object_name]
        cached_object = object_cache[random.randint(0, len(object_cache)-1)]

        if non_used_only:
            attempt_counter = 1
            while cached_object["status"] == "used" and attempt_counter < max_attempts:
                cached_object = object_cache[random.randint(
                    0, len(object_cache)-1)]
                attempt_counter += 1

        cached_object["status"] = "used"

        return cached_object["value"]

    def get_random_input_object(self, input_object_name):
        input_object_cache = self.cache["input_objects"][input_object_name]

        cached_input_object = input_object_cache[random.randint(
            0, len(input_object_cache)-1)]
        cached_input_object["status"] = "used"

        return cached_input_object

    def save(self, cache_type, object_name, value):

        self.cache[cache_type][object_name].append({
            "value": value,
            "status": "new"
        })

    def test_print_all_objects(self,):
        for i in self.cache["objects"]["Wallet"]:
            pprint(i)



test_response_data = {'data': {
                        'createUser': {
                            'id': '1',
                            'firstName': 'teststring!!!', 
                            'lastName': 'teststring', 
                            'description': 'teststring', 
                            'wallets': [{
                                'id': '3',
                                'name': 'test',
                                'currency': {},
                                'transactions': [{}],
                                'user': {},
                                'balance': "test"
                            },{
                                'id': '2',
                                'name': 'test',
                                'currency': {},
                                'transactions': [{}],
                                'user': {},
                                'balance': "test"
                            }], 
                            'friends': []}}}


test_schema = json.load(open('./introspection/testschema.json'))

cache = Cache(test_schema)

def get_base_type_detail(type_def):
    if type_def.get("ofType"):
        return get_base_type_detail(type_def["ofType"]) 
    else:
        return (type_def["kind"], type_def["name"])


def load_response_to_cache(response_data: dict, schema: dict, cache: Cache):
    '''
    Add return objects to cache recursively. 
    
    '''
    func_name = list(response_data["data"].keys())[0]
    func_res = response_data["data"][func_name]
    obj_type = ""

    # Search corresponding mutation/query in the schema.
    if func_name in schema["queries"]:
        obj_type = get_base_type_detail(schema["queries"][func_name]["type"])[1]
    elif func_name in schema["mutations"]:
        obj_type = get_base_type_detail(schema["mutations"][func_name]["type"])[1]

    load_response_to_cache_helper(func_res, schema, cache, obj_type)


def load_response_to_cache_helper(func_res: dict, schema: dict, cache: Cache, obj_type: str):
    # Store whole object to cache.
    cache.save("objects", obj_type, func_res)

    # Store Id in cache.
    if func_res.get("id"):
        cache.save("id", obj_type, func_res["id"])

    # Store child object in the cache.
    obj_fields = schema["objects"][obj_type]["fields"]

    for f in obj_fields:
        if get_base_type_detail(obj_fields[f])[0] == "OBJECT":
            child_obj_name = get_base_type_detail(obj_fields[f])[1]
            child_obj_details = func_res.get(f)

            # Check list or non-list.
            if isinstance(child_obj_details, list):
                for i in child_obj_details:
                    load_response_to_cache_helper(i, schema, cache, child_obj_name)
            elif isinstance(child_obj_details, dict):
                if child_obj_details:
                    load_response_to_cache_helper(child_obj_details, schema, cache, child_obj_name)



if __name__ == '__main__':
    load_response_to_cache(test_response_data, test_schema, cache)
    cache.test_print_all_objects()
    
    
