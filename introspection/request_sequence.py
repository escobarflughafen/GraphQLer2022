from process_functions import FunctionBuilder
from queue import Queue
import json 
from pprint import pprint

class RequestBuilder:
    def __init__(self, SCHEMAFILE, FUNCTIONLIST):
        # Read compiled schema files.
        schema_file = open(SCHEMAFILE, "r")
        schema_json = json.load(schema_file)

        # Read function list files.
        function_list_file = open(FUNCTIONLIST, "r")
        functions = function_list_file.readlines()
        
        self.fb = FunctionBuilder(schema_json)

        self.function_queue = Queue()
        self.request_sequence = []
        self.unsolved_function = []
        self.cache = []
        self.func_count = 0

        # Add the function name and type to the queue.
        for f in functions:
            func = f.split('\t')
            func_type = func[1].split('\n')

            self.function_queue.put((func[0], func_type[0]))
            self.func_count = self.func_count + 1

        # Add an marker to indicate the end of the queue.
        self.function_queue.put(0)

        '''
        self.function_list = {}

        for f in functions:
            args = f.split('\t')
            self.function_list[args[0]] = args[1]
        '''

    def print_function_list(self):
        while self.function_queue.qsize() > 1:
            print(self.function_queue.get())   
        print(self.func_count)

    
    # TODO: 1. build_sequence function: add create function first: only input object.
    # TODO: 2. Check into the input object: see is there any required ID field.
    # TODO: 2. add update fucntion: track cache (for any stored id).
    def create(self):
        create_func = self.fb.get_mutation_mapping_by_input_datatype()

        for i in create_func:
            print(i)
            self.request_sequence.append(i)

            # Check what object it generate and storeid


        


    def build_sequence(self):
        '''
        Start building function sequence.
        Return function dependency sequence & unsolved function
        '''

        '''
        while self.object_queue.qsize() > 1:
            ob = self.object_queue.get()

            # Reach the end of the round.
            if ob == 0:
                # Cannot release any object from the queue (cyclic dependency).
                if self.prev_object_count == self.object_queue.qsize():
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

        while not self.object_queue.empty():
            self.unsolved_object.append(self.object_queue.get())
        
        # TODO: User input path output file path.
        self.generate_object_sequence_file("./object_sequence.json")
        
        # Test remove later
        return (self.object_sequence, self.unsolved_object)
        
        '''
            
            

SCHEMAFILE = "neogeek_compiled.json"
OBJECTSEQFILE = "function_list.txt"
rb = RequestBuilder(SCHEMAFILE, OBJECTSEQFILE)
rb.create()

#rb.build_request_sequence()
#rb.print_request_sequence()