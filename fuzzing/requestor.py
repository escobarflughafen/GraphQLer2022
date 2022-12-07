from request.request import Request
from graphql_types.mutation import Mutation
from graphql_types.query import Query
import progressbar

from fuzzing.fuzzer.fuzzer import Fuzzer
from graphql_types.process_functions import FunctionBuilder


def is_dynamic_parameter(arg):
    return arg["kind"] == "SCALAR" and arg["name"] == 'ID'


def traverse_response(response, callback, schema, function_type="Create"):
    try:
        response_data = response["data"]
        for function_name in response_data:
            if function_name in schema["queries"]:
                traverse_query(
                    function_name, response_data[function_name], callback, schema)
            elif function_name in schema["mutations"]:
                traverse_mutation(
                    function_name, response_data[function_name], callback, schema, function_type=function_type)
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


def traverse_mutation(mutation_name, data, callback, schema, function_type="Create"):
    mutation_schema = schema["mutations"][mutation_name]
    return_type = mutation_schema["type"]
    if return_type["kind"] == "OBJECT":
        oftype = return_type["name"]
        traverse_object(oftype, data, callback, schema, function_type=function_type)
    elif return_type["kind"] == "LIST":
        oftype = return_type["ofType"]["name"]
        traverse_list(oftype, data[mutation_name], callback, schema, function_type=function_type)


def traverse_list(oftype, data, callback, schema, function_type="Create"):
    for item in data:
        traverse_object(oftype, item, callback, schema,function_type=function_type)


object_types = ['OBJECT', 'INTERFACE']


def traverse_object(oftype, data, callback, schema, function_type="Create"):
    if oftype in schema["objects"]:
        #cache.save("objects", oftype, data)
        if function_type != "Delete":
            callback('objects', oftype, data, function_type=function_type)

    object_schema = schema["objects"][oftype]
    field_schema = object_schema["fields"]
    for field in data:
        field_define = field_schema[field]
        field_kind = field_define["kind"]
        field_typename = field_define["name"]
        if field_kind == "SCALAR":
            if field_typename == 'ID':
                callback('id', oftype, None, data[field], function_type)
                callback('unique_objects', oftype, data, data[field], function_type)
                if function_type == "Delete":
                    return
            else:
                callback(field_typename, oftype, [field, data[field]], function_type=function_type)

        elif field_kind == 'LIST':
            _oftype = field_define["ofType"]["name"]
            # TODO: resolve scalars
            traverse_list(_oftype, data[field], callback, schema, function_type=function_type)

        elif field_kind == 'OBJECT':
            traverse_object(field_typename, data[field], callback, schema, function_type=function_type)


class Requestor:
    def __init__(self, req_seq, cache, fuzzer: Fuzzer, url, schema, function_builder: FunctionBuilder):
        self.req_seq = req_seq
        self.cache = cache
        self.fuzzer = fuzzer
        self.url = url
        self.schema = schema
        self.current_id_oftype = ''
        self.function_builder = function_builder
        self.errors = []

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

    def handle_error(self, response):
        self.errors.append(response)
        return 0

    def execute(self, schema):
        for func in progressbar.progressbar(self.req_seq):
            #print("NOW TESTING:", func)
            is_mutation = func in schema["mutations"]
            is_query = func in schema["queries"]

            if is_mutation:
                func_schema = schema["mutations"][func]
                MODE = Request.MODE_MUTATION
                func_instance = Mutation(
                    func,
                    schema_json=func_schema,
                    args_schema=self.function_builder
                    .build_function_call_schema(MODE, func)
                )
            elif is_query:
                func_schema = schema["queries"][func]
                MODE = Request.MODE_QUERY
                func_instance = Query(
                    func,
                    schema_json=func_schema,
                    args_schema=self.function_builder
                    .build_function_call_schema(MODE, func)
                )
            else:
                raise Exception(f"cannot find function in GraphQL schema")

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
            #print(func_instance.stringify_payload())

            response = req_instance.request()
            #print(func, '\n', response)

            # TODO: store in cache
            # assigned
            def save_in_cache(cache_type, object_name, value=None, id=None, function_type="Create"):
                if id and function_type == "Delete":
                    self.cache.delete(object_name, id)
                else:
                    self.cache.save(cache_type, object_name, value, id)

            # TODO: resolve response & error handling
            
            if 'errors' in response:
                self.handle_error(response)
            else:
                if MODE == Request.MODE_QUERY:
                    traverse_response(response, save_in_cache, schema)
                else:
                    traverse_response(response, save_in_cache, schema, func_instance.args_schema[func]["functionType"])

