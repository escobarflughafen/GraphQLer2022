from queue import Queue
import json


#SCHEMAPATH = "./introspection/schema.json"
SCHEMAPATH = "./introspection/shopify_schema.json"

class ObjectSequenceBuilder:
    def __init__(self, SCHEMAPATH):
        self.object_schema = json.load(open(SCHEMAPATH))["objects"]
        self.object_queue = Queue()
        self.object_sequence = []

        self.prev_object_count = 0

        # Add the name of all data type to the queue.
        for dt in self.object_schema:
            self.object_queue.put(dt)
            self.prev_object_count = self.prev_object_count + 1

        # Add an marker to indicate the end of the queue.
        self.object_queue.put(0)
        print("Initial object counts:")
        print(self.prev_object_count)
        print()


    def get_base_type_detail(self, type_def):
        '''
        Return object base type and name and non-null attribute.
        '''
        if type_def.get("ofType"):
            return self.get_base_type_detail(type_def["ofType"]) 
        else:
            if type_def.get("nonNull"): 
                return (type_def["kind"], type_def["name"], True)
            else:
                return (type_def["kind"], type_def["name"], False)


    def get_consume(self, object_name):
        '''
        Take an object name
        Check what other object data types it consumes or depends on
        Return the list of objects it consumes (or empty list if none)
        ''' 
        consume_list = []
        params = self.object_schema[object_name]["fields"]
        for p_name, p_detail in params.items():
            base_type, ob_name, non_null = self.get_base_type_detail(p_detail)

            if base_type == "OBJECT" and non_null is True:
                consume_list.append(ob_name)
        return consume_list


    def is_object_exist(self, object_list):
        '''
        Check if all the objects exist in the object sequence list at this point.
        If all exist return true, otherwise return false.
        '''
        for o in object_list:
            if o not in self.object_sequence:
                return False
        return True


    def build_sequence(self):
        '''
        Start building object sequence.
        Return object dependency sequence (list) & unsolved objects (queue) 
        '''
        while self.object_queue.qsize() > 1:
            ob = self.object_queue.get()

            # Reach the end of the round.
            if ob == 0:
                # Cannot release any object from the queue (cyclic dependency).
                if self.prev_object_count == self.object_queue.qsize():
                    print("Unsolve objects count:")
                    print(self.prev_object_count)
                    print()
                    break
                else:
                    self.prev_object_count = self.object_queue.qsize()
                    self.object_queue.put(0)
            else:
                consume_list = self.get_consume(ob)
                if not consume_list:
                    self.object_sequence.append(ob)
                else:
                    if self.is_object_exist(consume_list):
                        self.object_sequence.append(ob)
                    else:
                        self.object_queue.put(ob)

        return (self.object_sequence, self.object_queue)