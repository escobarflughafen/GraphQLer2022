import yaml
from request.request import Request
from graphql_types.callable import Callable
from fuzzing.fuzzer.fuzzer import Fuzzer

def is_dynamic_parameter(arg):
    return arg["kind"] == "SCALAR" and arg["name"] == 'ID'

def traverse_response(response, callback, schema):
    try:
        response_data = response["data"]
        for function_name in response_data:
            if function_name in schema["queries"]:
                traverse_query(function_name, response_data[function_name], callback, schema)
            elif function_name in schema["mutations"]:
                traverse_mutation(function_name, response_data[function_name], callback, schema)
    except Exception:
        pass

def traverse_query(query_name, data, callback, schema):
    query_schema = schema["queries"][query_name]
    return_type = query_schema["type"]
    if return_type["kind"] == "OBJECT":
        oftype = return_type["name"]
        traverse_object(oftype, data[query_name], callback, schema)
    elif return_type["kind"] == "LIST":
        oftype = return_type["ofType"]["name"]
        traverse_list(oftype, data, callback, schema)
    
def traverse_mutation(mutation_name, data, callback, schema):
    mutation_schema = schema["mutations"][mutation_name]
    return_type = mutation_schema["type"]
    if return_type["kind"] == "OBJECT":
        oftype = return_type["name"]
        traverse_object(oftype, data, callback, schema)
    elif return_type["kind"] == "LIST":
        oftype = return_type["ofType"]["name"]
        traverse_list(oftype, data[mutation_name], callback, schema)

def traverse_list(oftype, data, callback, schema):
    print(oftype)
    for item in data:
        traverse_object(oftype, item, callback, schema) 

object_types = ['OBJECT', 'INTERFACE']

def traverse_object(oftype, data, callback, schema):
    #handle IDs
    '''
    if isinstance(oftype, list) and len(oftype) == 2:
        if oftype[0] == id:
            callback('id', oftype, data)
        return
    '''
    if oftype in schema["objects"]:
        #cache.save("objects", oftype, data)
        callback('objects', oftype, data)

    object_schema = schema["objects"][oftype]
    field_schema  = object_schema["fields"]
    for field in data:
        field_define = field_schema[field]
        field_kind = field_define["kind"]
        field_typename = field_define["name"]
        if field_kind == "SCALAR":
            if field_typename == 'ID':
                callback('id', oftype, data[field])
            else:
                callback(field_typename, oftype, [field, data[field]])

        elif field_kind == 'LIST':
            _oftype = field_define["ofType"]["name"]
            #TODO: resolve scalars
            traverse_list(_oftype, data[field], callback, schema)

        elif field_kind == 'OBJECT':
            traverse_object(field_typename, data[field], callback, schema)
            

class Requestor:
    def __init__(self, req_seq, cache, fuzzer: Fuzzer, url, schema):
        self.req_seq = req_seq
        self.cache = cache
        self.fuzzer = fuzzer
        self.url = url
        self.schema = schema
        self.current_id_oftype = ''
        #self.load_query_inputs(query_inputs)
        #self.load_mutation_inputs(mutation_inputs)
    
    #def load_query_inputs(self, query_inputs):
        #if isinstance(query_inputs, dict):
            #self.query_inputs = query_inputs
        #elif isinstance(query_inputs, str):
            #self.query_inputs = yaml.load(open(query_inputs))
        #else:
            #self.query_inputs = yaml.load(query_inputs)


    #def load_mutation_inputs(self, mutation_inputs):
        #if isinstance(mutation_inputs, dict):
            #self.mutation_inputs = mutation_inputs
        #elif isinstance(mutation_inputs, str):
            #self.mutation_inputs = yaml.load(open(mutation_inputs))
        #else:
            #self.mutation_inputs = yaml.load(mutation_inputs)

        

    def concretize_args(self, args):
        for arg in args:
            if isinstance(args[arg], dict):
                self.concretize_args(args[arg])
            else:
                self.concretize_arg(args[arg])


    def concretize_arg(self, arg):
        if isinstance(arg, dict):
            self.concretize_args(self, arg)
        elif isinstance(arg, list):
            print(arg)
            if len(arg) == 1:
                self.concretize_arg(arg[0])
            else:
                if arg[1] == 'Int':
                    arg[0] = self.fuzzer.resolve_int(arg)
                elif arg[1] == 'Float':
                    arg[0] = self.fuzzer.resolve_float(arg)
                elif arg[1] == 'String':
                    arg[0] = self.fuzzer.resolve_string(arg)
                elif arg[1] == 'Enum':
                    arg[0] = self.fuzzer.resolve_enum(arg)
                elif arg[1] == 'ID':
                    id_of_type = arg[2]
                    
                    arg[0] = self.fuzzer.resolve_id(id_of_type)
                    #arg[0] = self.fuzzer.resolve_id(arg)

                else:
                    raise Exception(
                        f"error in concretizing function argument {arg}")

    def execute(self, schema):
        for func in self.req_seq:
            print("NOW TESTING:", func)
            if func in schema["mutations"]:
                func_schema = schema["mutations"][func]
                MODE = Request.MODE_MUTATION
            elif func in schema["queries"]:
                func_schema = schema["queries"][func]
                MODE = Request.MODE_QUERY
            else:
                raise Exception(f"cannot find function in GraphQL schema")

            func_instance = Callable(func, schema_json=func_schema)

            func_instance.prepare_payload(schema)

            prepared_args = func_instance.prepared_payload["args"]
            return_kind = func_schema["type"]["kind"]
            if return_kind == 'LIST':
                self.current_id_oftype = func_schema["type"]["ofType"]["name"]
            else:
                self.current_id_oftype = func_schema["type"]["name"]

            self.concretize_args(prepared_args)

            # TODO: make request
            req_instance = Request(self.url, MODE)
            payload_string = func_instance.stringify_payload()
            req_instance.add_payload(payload_string)
            print(func_instance.stringify_payload())

            response = req_instance.request()
            print(func, '\n', response)

            # TODO: store in cache
            # assigned
            def save_in_cache(cache_type, object_name, value):
                self.cache.save(cache_type, object_name, value)
                
            traverse_response(response, save_in_cache, schema)
            
            # TODO: error handling

