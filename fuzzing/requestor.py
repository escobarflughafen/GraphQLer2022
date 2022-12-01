import sys, os, random
from request.request import Request
from graphql_types.callable import Callable
from fuzzing.fuzzer.fuzzer import Fuzzer

def is_dynamic_parameter(arg):
    return arg["kind"] == "SCALAR" and arg["name"] == 'ID'

class Requestor:
    def __init__(self, req_seq, cache, fuzzer: Fuzzer, url):
        self.req_seq = req_seq
        self.cache = cache
        self.fuzzer = fuzzer
        self.url = url

    def concretize_args(self, args, graphql_schema):
        for arg in args:
            if isinstance(args[arg], dict):
                self.concretize_args(args[arg], graphql_schema)
            else:
                self.concretize_arg(args[arg], graphql_schema)
                
                        
    def concretize_arg(self, arg, graphql_schema):
        if isinstance(arg, dict):
            self.concretize_args(self, arg, graphql_schema)
        elif isinstance(arg, list):
            if len(arg) == 1:
                self.concretize_arg(arg[0], graphql_schema)
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
                    arg[0] = 'TESTIDTESTIDTESTID'
                    #arg[0] = self.fuzzer.resolve_id(arg)
            
                else:
                    raise Exception(f"error in concretizing function argument {arg}")

                
            

    def execute(self, schema):
        for func in self.req_seq:
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
            self.concretize_args(prepared_args, schema)
            

            # TODO: make request 
            req_instance = Request(self.url, MODE)
            print(func_instance.stringify_payload())
            req_instance.add_payload(func_instance.stringify_payload())
            
            #print(req_instance.get_request_body())

            response = req_instance.request()

            # TODO: store in cache
            # assigned
            print(response)

            # TODO: error handling

    '''
    def execute(self, schema):
        for reqname in self.req_seq:
            if reqname in schema["queries"]:
                mode = Request.MODE_QUERY
            elif reqname in schema["mutations"]:
                mode = Request.MODE_MUTATION
            else:
                raise Exception('Invalid request type - ')
            req = Request(self.url, mode, )
            
        return 
    '''