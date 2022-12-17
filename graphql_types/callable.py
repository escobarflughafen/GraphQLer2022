from graphql_types import datatype


def get_type(type):
    if type["name"] == None:
        return get_type(type["ofType"])
    else:
        return type


class Callable(datatype.Datatype):
    """
    Abstracting Query and Mutation Type
    """

    def __init__(self, name, schema_json=None, args_schema=None):
        super().__init__(
            name,
            schema_json=schema_json,
        )
        self.args_schema = args_schema

    def prepare_payload(self, gql_server_schema):
        '''
        generate a unfulfilled dict for arguments and return fields
        '''

        def prepare_input_object(arg, all_input_objects):
            #input_object = all_input_objects[arg["name"]]
            processed_input_object = {}
            fields = arg["args"]

            for field in fields:
                if fields[field]["kind"] == "INPUT_OBJECT":
                    processed_input_object[field] = prepare_input_object(
                        fields[field], all_input_objects)
                elif fields[field]["kind"] == 'LIST':
                    processed_input_object[field] = prepare_list(
                        fields[field]["ofType"], all_input_objects)
                else:
                    processed_input_object[field] = prepare_scalar(
                        fields[field], all_input_objects)

            return processed_input_object

        def prepare_args(args, all_input_objects):
            prepared_args = {}
            if not args:
                return prepared_args

            for arg in args:
                if args[arg]["kind"] == "INPUT_OBJECT":
                    prepared_args[arg] = prepare_input_object(
                        args[arg], all_input_objects
                    )
                elif args[arg]["kind"] == "LIST":
                    prepared_args[arg] = prepare_list(
                        args[arg]["ofType"], all_input_objects)
                else:
                    prepared_args[arg] = prepare_scalar(
                        args[arg], all_input_objects)

            return prepared_args

        def prepare_scalar(arg, all_input_objects):
            if arg["name"] == "ID":
                return [None, 'ID', arg["ofDatatype"]]

            return [None, arg["name"]]

        def prepare_list(arg, all_input_objects):
            prepared_list = []

            if arg["kind"] == "LIST":
                prepared_list.append(prepare_list(
                    arg["ofType"], all_input_objects))
            elif arg["kind"] == "INPUT_OBJECT":
                prepared_list.append(
                    prepare_input_object(arg, all_input_objects))
            else:
                prepared_list.append(prepare_scalar(arg, all_input_objects))

            return prepared_list

        def prepare_return_fields(return_type, all_objects, max_depth=3):
            '''
                return all fields of return object
            '''
            prepared_return_fields = {}

            def traverse_fields(prepared_return_fields, fields, all_objects, max_depth):
                if max_depth == 0:
                    return

                for field in fields:
                    if fields[field]["kind"] == 'OBJECT':
                        child_obj_fields = all_objects[fields[field]
                                                       ["name"]]["fields"]
                        child_obj_query_fields = {}
                        prepared_return_fields[field] = child_obj_query_fields
                        traverse_fields(
                            child_obj_query_fields, child_obj_fields, all_objects, max_depth-1)

                    elif fields[field]["kind"] == 'LIST':
                        # TODO: Process SCALAR & ENUMS
                        # TODO: Recursively resolve lists 120922
                        of_type = get_type(fields[field]["ofType"])
                        if of_type["kind"] == 'OBJECT':
                            child_obj = all_objects[of_type["name"]]
                            child_obj_query_fields = {}
                            prepared_return_fields[field] = child_obj_query_fields
                            traverse_fields(
                                child_obj_query_fields, child_obj["fields"], all_objects, max_depth-1)
                        else:
                            prepared_return_fields[field] = True

                    elif fields[field]["kind"] == 'INTERFACE':
                        pass
                    else:
                        prepared_return_fields[field] = True

            if return_type["kind"] == 'OBJECT':
                obj = all_objects[return_type["name"]]
                fields = obj["fields"]
                traverse_fields(prepared_return_fields,
                                fields, all_objects, max_depth)
            elif return_type["kind"] == 'LIST':
                obj = all_objects[return_type["ofType"]["name"]]

                fields = obj["fields"]
                traverse_fields(prepared_return_fields,
                                fields, all_objects, max_depth)

            return prepared_return_fields

        self.prepared_payload = {
            "args": prepare_args(self.args_schema[self.name]["args"], gql_server_schema['inputObjects']),
            "fields": prepare_return_fields(self.schema["type"], gql_server_schema['objects'])
        }


    def stringify_payload(self):
        '''
        return payload as string for request.request.sequence
        '''
        prepared_payload = self.prepared_payload
        payload_str = ""
        payload_str += self.name

        def dump_args(args, ):
            # print(args)
            arg_str = ''
            if args:
                for arg in args:
                    arg_str += arg + ': '
                    if isinstance(args[arg], dict):
                        arg_str += '{'
                        dump_args(args[arg])
                        arg_str += '},'
                    else:
                        if isinstance(args[arg], list):
                            if len(args[arg]) == 2 or len(args[arg]) == 3:
                                if args[arg][1] in ['String', 'ID']:
                                    arg_str += '"' + str(args[arg][0]) + '"'
                                else:
                                    arg_str += str(args[arg][0])
                            elif len(args[arg]) == 1:
                                arg_str += '['
                                arg_str += str(args[arg][0])
                                arg_str += ']'
                    arg_str += ', '
            return arg_str

        if prepared_payload["args"]:
            payload_str += '('
            payload_str += dump_args(prepared_payload["args"])
            payload_str += ')'

        def dump_field_str(fields, tabs=1):
            field_str = "{\n"
            if fields:
                for field in fields:
                    if isinstance(fields[field], dict):
                        if len(fields[field]) > 0:
                            field_str += '\t'*tabs + \
                                str(field) + ' ' + \
                                dump_field_str(fields[field], tabs+1) + '\n'
                    else:
                        field_str += '\t'*tabs + str(field)+'\n'
            field_str += '\t'*tabs + "}"
            return field_str

        payload_str += dump_field_str(prepared_payload["fields"])

        return payload_str
