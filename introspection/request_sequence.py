from process_functions import FunctionBuilder
from queue import Queue
import json 
from pprint import pprint

class RequestBuilder:
    def __init__(self, SCHEMAFILE, FUNCTIONLIST):
        # Read compiled schema files.
        schema_file = open(SCHEMAFILE, "r")
        self.schema_json = json.load(schema_file)

        # Read function list files.
        function_list_file = open(FUNCTIONLIST, "r")
        functions = function_list_file.readlines()

        # Read mutation list from schema. 
        self.mutation = self.schema_json["mutations"]

        self.fb = FunctionBuilder(self.schema_json)

        self.create_function_q = Queue()
        self.update_function_q = Queue()
        self.delete_function_q = Queue()

        self.create_func_count = 0
        self.update_func_count = 0
        self.delete_func_count = 0

        self.read_functions(functions)

        # Add an marker to indicate the end of the queue.
        self.create_function_q.put(0)
        self.update_function_q.put(0)
        self.delete_function_q.put(0)

        self.request_sequence = []
        self.unsolved_function = []
        self.cache = []


    '''
    def print_function_list(self):
        while self.function_q.qsize() > 1:
            print(self.function_q.get())   
        print(self.func_count)
    '''
    
    # TODO: 1. build_sequence function: add create function first: only input object.
    # TODO: 2. Check into the input object: see is there any required ID field.
    # TODO: 2. add update fucntion: track cache (for any stored id).
    def create_functions(self):
        '''
        Put all functions with action type CREATE in to the request sequence. 
        '''

        while self.create_function_q.qsize() > 1:
            curr_func = self.create_function_q.get()

            # Reach the end of the round.
            if curr_func == 0:
                # Cannot release any object from the queue.
                if self.create_func_count == self.create_function_q.qsize():
                    break
                else:
                    self.create_func_count = self.create_function_q.qsize()
                    self.create_function_q.put(0)
            else:
                args = self.get_args("createUser")

                '''
                consume_list = self.get_consume(ob)
                if not consume_list:
                    self.object_sequence.append(ob)
                else:
                    if self.is_object_exist(consume_list):
                        self.object_sequence.append(ob)
                    else:
                        self.object_queue.put(ob)
                '''


            '''independent_func = self.fb.get_mutation_mapping_by_input_datatype()

            for i in independent_func:
                print(i)
                self.request_sequence.append(i)'''


    def get_args(self, function_name):
        pprint(self.mutation[function_name])
        return



                


    def read_functions(self, function_list):
        '''
        Read all function from the files,
        and classify those function based on the action type.
        '''
        # Add the function name and type to the queue.
        for f in function_list:
            func = f.split('\t')
            func_type = func[1].split('\n')

            # Categorize based on action type.
            if func_type[0].upper() == "CREATE":
                self.create_function_q.put(func[0])
                self.create_func_count = self.create_func_count + 1
            elif func_type[0].upper() == "UPDATE":
                self.update_function_q.put(func[0])
                self.update_func_count = self.update_func_count + 1
            elif func_type[0].upper() == "DELETE":
                self.delete_function_q.put(func[0])           
                self.delete_func_count = self.delete_func_count + 1
    

        


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
rb.create_functions()

#rb.build_request_sequence()
#rb.print_request_sequence()