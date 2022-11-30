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

    
    def prepare_payload(self, all_input_objects, all_objects):
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
                    if fields[field]["type"] == 'OBJECT':
                        child_obj_fields = all_objects[fields[field]["name"]]["fields"]
                        traverse_fields(prepared_return_fields, child_obj_fields, max_depth-1)

                    elif fields[field]["type"] == 'LIST':
                        traverse_fields(prepared_return_fields, fields[field]["ofType"], all_objects, max_depth-1)

                    elif fields[field]["type"] == 'INTERFACE':
                        pass
                    else:
                        prepare_return_fields[field] = True
            
            if return_type["kind"] == 'OBJECT':
                obj = all_objects[return_type["name"]]
                fields = obj["field"]
                traverse_fields(prepared_return_fields, fields, all_objects)
            
            return prepared_return_fields


        self.prepared_payload = {
            "args": prepare_args(self.schema["args"], all_input_objects),
            "fields": prepare_return_fields(self.schema["type"], all_objects)
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
        
        def dump_field_str(fields):
            field_str = "{"
            if fields:
                for field in fields:
                    field_str += str(field)+'\n'
            field_str += "}"
            return field_str
            
        payload_str += dump_field_str(prepared_payload["fields"])

        return payload_str
                    

