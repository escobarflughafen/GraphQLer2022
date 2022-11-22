import json

class FunctionBuilder:
    def __init__(self, schema_json):
        self.schema_json = schema_json
        self.objects = schema_json["objects"]
        self.input_objects = schema_json["inputObjects"]
        if schema_json.get("queries") != None:
            self.queries = schema_json["queries"]
            self.query_datatype_mappings = self.link_functions_with_datatype("queries")
        if schema_json.get("mutations") != None:
            self.mutations = schema_json["mutations"]
            self.mutation_datatype_mappings = self.link_functions_with_datatype("mutations")

    def get_query_mappings(self):
        return self.query_datatype_mappings

    def get_mutation_mappings(self):
        return self.mutation_datatype_mappings

    def get_query_mapping(self, query_name):
        return self.query_datatype_mappings[query_name]

    def get_mutation_mapping(self, mutation_name):
        return self.mutation_datatype_mappings[mutation_name]

    def link_functions_with_datatype(self, category):
        list = {}
        function_objects = self.schema_json[category]

        # we review every functions
        for function_name, function_body in function_objects.items():
            input_args = function_body["args"]
            output = function_body["type"]
            # to bypass any status like LIST, only get real OBJECT
            output_data_type = self._get_type(output)

            # Since I assume every output is actually an Object, so I actually did not check for any other datatypes.
            if output_data_type["kind"] == "OBJECT":
                list[function_name] = {}
                # here I just copy the raw data just in case
                list[function_name]["rawdata"] = function_body
                list[function_name]["inputDatatype"] = {}

                # since the output will be a single Object, we just copy its original structure here
                list[function_name]["outputDatatype"] = output_data_type

                # then we check for any input items and see if it match any of the Objects
                for arg_name, arg_body in function_body["args"].items():
                    # again we only focus on the real Object, not the status like LIST or something
                    arg_data_type = self._get_type(arg_body)
                    # if the scalar type is ID, then we want to find if there's any ID exists
                    # in the output datatype. If exists, we will assume that the input ID here 
                    # is related to one of the output datatype (we search recursively for every 
                    # child objects inside the output object).
                    if arg_data_type["kind"] == "SCALAR" and arg_data_type["name"] == "ID":
                        list[function_name]["inputDatatype"][arg_name] = self._search_related_object(arg_name, output_data_type["name"])
                    # if it is other scalar or enum type we will search the scalar-datatype list
                    # to look for matching names.
                    elif arg_data_type["kind"] == "SCALAR" or arg_data_type["kind"] == "ENUM":
                        list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                    # Otherwise if it is an input object, we want to know if there's any ID type
                    # inside the input object. Then we are basically doing similar things by searching
                    # inside the output datatype and find the mapping.
                    elif arg_data_type["kind"] == "INPUT_OBJECT":
                        list[function_name]["inputDatatype"][arg_name] = self._search_related_object_from_input_object(arg_data_type["name"], arg_name, output_data_type["name"])

            elif output_data_type == "SCALAR":
                pass
            elif output_data_type == "INTERFACE":
                pass
            elif output_data_type == "UNION":
                pass
            elif output_data_type == "ENUM":
                pass
            elif output_data_type == "INPUT_OBJECT":
                pass

        return list


    # Function to bypass any status like LIST or something
    # return the true type of the data
    def _get_type(self, type):
        if type["name"] == None:
            return self._get_type(type["ofType"])
        else:
            return type

    def _search_related_object(self, id_name, object_name):
        result = None
        output_objects = self.objects
        # in the first loop we check for scalar type only
        # we should have check all scalar type before checking any objects to prevent
        # the program bypass any IDs existing in current datatype
        for arg_name, arg_body in output_objects[object_name]["fields"].items():
            arg_body = self._get_type(arg_body)
            if arg_body["kind"] == "SCALAR" and arg_body["name"] == "ID":
                result = object_name
                return result
        
        # then if there are no ID type scalar exists we then go through objects
        # inside to do further check
        for arg_name, arg_body in output_objects[object_name]["fields"].items():
            arg_body = self._get_type(arg_body)
            if arg_body["kind"] == "OBJECT":
                result = self._search_related_object(id_name, arg_body["name"])
                if result != None:
                    return result

        # then if we find nothing we return None
        return None


    def _search_related_object_from_input_object(self, input_object_datatype, id_name, output_object_name):
        result = None
        input_objects = self.input_objects
        # we check for every object inside the input object and see if it is an ID type
        for input_object_name, input_object_body in input_objects[input_object_datatype]["fields"].items():
            input_object_body = self._get_type(input_object_body)
            # if we found and ID type directlly, we call the function to search from the output object name isntantly
            if input_object_body["kind"] == "SCALAR" and input_object_body["name"] == "ID":
                return self._search_related_object(input_object_name, output_object_name)
            # else we have to check the child input objects and do the recursive thing
            # here we did not instantly return is because the function have to search for 
            # every objects instead of the first one.
            elif input_object_body["kind"] == "INPUT_OBJECT":
                result = self._search_related_object_from_input_object(input_object_body["name"], input_object_name, output_object_name)
        return result


    def _link_objects_with_data_type(self):
        list = {}
        for object_name, object_body in self.objects.items():
            for field_name, field_value in object_body["fields"].items():
                field_value = self._get_type(field_value)
                list[field_name] = {}
                list[field_name]["kind"] = field_value["kind"]
                list[field_name]["name"] = object_name
        return list

    def _get_scalar_with_datatype(self, name):
        objects_scalar = self._link_objects_with_data_type()
        input_objects_scalar = self._link_objects_with_data_type()
        list = {}
        objects_scalar.update(input_objects_scalar)
        if objects_scalar.get(name) != None:
            return objects_scalar[name]["name"]
        else:
            return None




f = open("schema.json", "r")
objects = json.load(f)

test = FunctionBuilder(objects)
test1 = test.get_query_mappings()
test2 = test.get_mutation_mappings()
test4 = test.get_query_mapping("customer")
test5 = test.get_mutation_mapping("checkoutCompleteFree")
test3 = ""

