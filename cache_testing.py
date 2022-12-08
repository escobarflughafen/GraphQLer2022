import random
import json

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


test_response_data = {'data': {'createUser': {'id': 'c04539ff-f88d-4b03-9eda-5b4df555ef51',
                                              'firstName': 'teststring', 'lastName': 'teststring', 'description': 'teststring', 'wallets': [], 'friends': []}}}


test_schema = json.load(open('./testschema.json'))

cache = Cache(test_schema)


def load_response_to_cache(response_data: dict, schema: dict, cache: Cache):
    # TODO: write response parser, use `test_response_data` & `test_schema`

    pass


if __name__ == '__main__':
    # TODO: test here
    pass