import random
import os
import sys


class Cache:
    def __init__(self, schema):
        self.schema = schema

        self.cache = {
            "id": {
                objname: {} for objname in schema["objects"]
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

    def get_random_id_by_type(self, object_name):
        '''
            randomly return a id for a certain object type in the cache 
        '''
        id_cache = list(self.cache["id"][object_name].keys())

        if len(id_cache) == 0:
            return None

        index = random.randint(0, max(len(id_cache)-1, 0))

        cached_object = id_cache[index]

        return cached_object

    def get_object_by_id(self, object_name, id):
        '''
            return a object by id of certain object type 
        '''
        unique_object_cache = self.cache["unique_objects"]

        if id in unique_object_cache:
            return unique_object_cache[object_name][id]

        return None

    def get_random_object(self, object_name, non_used_only=False, max_attempts=1000):
        '''
            return a random object by object name
        '''
        object_cache = self.cache["objects"][object_name]
        if len(object_cache) == 0:
            return None

        index = random.randint(0, len(object_cache)-1)
        cached_object = object_cache[index]


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

    def save(self, cache_type, object_name, value=None, id=None):
        #if unique:
            #self.cache['unique_objects'][object_name][value] = data
        if id:
            self.cache["id"][object_name][id] = True
            if value:
                self.cache['unique_objects'][object_name][id] = value
        elif value:
            self.cache[cache_type][object_name].append(value)
    
    def delete(self, object_name, id):
        try:
            self.cache["id"][object_name].pop(id)
            self.cache["unique_objects"][object_name].pop(id)
        except Exception:
            pass
        

