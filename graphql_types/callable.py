from graphql_types import datatype


class Callable(datatype.Datatype):
    """
    Abstracting Query and Mutation Type
    """

    def __init__(self, name, schema_json=None, introspection_json=None, sdl=None):
        super().__init__(
            name,
            schema_json=schema_json,
            introspection_json=introspection_json,
            sdl=sdl
        )

    
    def prepare_payload(self, parsed_graphql_schema):
        '''
        generate a unfulfilled dict for arguments and return fields
        '''
        def process_input_object(input_object, all_input_objects):
            processed_input_object = {}
            fields = input_object["fields"]

            for field in fields:
                if fields[field]["kind"] == "INPUT_OBJECT":
                    processed_input_object[field] = process_input_object(all_input_objects[fields[field]["name"]])
                else:
                    processed_input_object[field] = None
            
            return processed_input_object


        def prepare_args(args, all_input_objects):
            prepared_args = {}
            if not args:
                return None

            for arg in args:
                if args[arg]["kind"] == "INPUT_OBJECT":
                    prepared_args[arg] = process_input_object(all_input_objects[args[arg]["name"]])
                elif args[arg]["kind"] == "LIST":
                    prepared_args[arg] = []
                else:
                    prepared_args[arg] = ''
            
            return prepared_args
        
        def prepare_return_fields(return_type, all_objects, max_depth = 3):
            '''
                return all fields of return object
            '''
            prepared_return_fields = {}

            def traverse_fields(prepared_return_fields, fields, all_objects, max_depth):
                if max_depth == 0:
                    return

                for field in fields:
                    if fields[field]["kind"] == 'OBJECT':
                        child_obj_fields = all_objects[fields[field]["name"]]["fields"]
                        child_obj_query_fields = {}
                        prepared_return_fields[field] = child_obj_query_fields
                        traverse_fields(child_obj_query_fields, child_obj_fields, all_objects, max_depth-1)

                    elif fields[field]["kind"] == 'LIST':
                        child_obj = all_objects[fields[field]["ofType"]["name"]]
                        child_obj_query_fields = {}
                        prepared_return_fields[field] = child_obj_query_fields
                        traverse_fields(child_obj_query_fields, child_obj["fields"], all_objects, max_depth-1)

                    elif fields[field]["kind"] == 'INTERFACE':
                        pass
                    else:
                        prepared_return_fields[field] = True
            
            if return_type["kind"] == 'OBJECT':
                obj = all_objects[return_type["name"]]
                fields = obj["fields"]
                traverse_fields(prepared_return_fields, fields, all_objects, max_depth)
            elif return_type["kind"] == 'LIST':
                obj = all_objects[return_type["ofType"]["name"]]
                
                fields = obj["fields"]
                traverse_fields(prepared_return_fields, fields, all_objects, max_depth)
            
            return prepared_return_fields


        self.prepared_payload = {
            "args": prepare_args(self.schema["args"], parsed_graphql_schema['inputObjects']),
            "fields": prepare_return_fields(self.schema["type"], parsed_graphql_schema['objects'])
        }
    
    def stringify_payload(self, prepared_payload):
        '''
        return payload as string for request.request.sequence
        '''

        payload_str = ""
        payload_str += self.name

        arg_str = '('
        def dump_args(args):
            if args: 
                for arg in args:
                    arg_str += arg + ': '
                    if isinstance(args[arg], dict):
                        arg_str += '{'
                        dump_args(args[arg])
                        arg_str += '},'
                    else:
                        if isinstance(args[arg], str):
                            arg_str += '"'
                            arg_str += args[arg]
                            arg_str += '"'
                        else:
                            arg_str += str(args[arg])
                
        if prepared_payload["args"]:
            dump_args(prepared_payload["args"]) 
            arg_str += ')'
            payload_str += arg_str
        
        def dump_field_str(fields, tabs=1):
            field_str = "{\n"
            if fields:
                for field in fields:
                    if isinstance(fields[field], dict):
                        if len(fields[field]) > 0:
                            field_str += '\t'*tabs + str(field) + ' ' + dump_field_str(fields[field], tabs+1) + '\n'
                    else:
                        field_str += '\t'*tabs + str(field)+'\n'
            field_str += '\t'*tabs + "}"
            return field_str
            
        payload_str += dump_field_str(prepared_payload["fields"])

        return payload_str
                    
