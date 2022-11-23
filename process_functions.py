import json
import re


class FunctionBuilder:

    def __init__(self, schema_json, function_list_file_path = None, query_datatype_file_path = None, mutation_datatype_file_path = None):
        self.schema_json = schema_json
        self.objects = schema_json["objects"]
        self.input_objects = schema_json["inputObjects"]
        if schema_json.get("queries") != None and query_datatype_file_path == None:
            self.queries = schema_json["queries"]
            self.query_datatype_mappings = self.link_functions_with_datatype("queries")
        elif query_datatype_file_path != None:
            f = open(query_datatype_file_path, 'r')
            self.query_datatype_mappings = json.load(f)
            f.close()
        if schema_json.get("mutations") != None and mutation_datatype_file_path == None:
            self.mutations = schema_json["mutations"]
            self.mutation_datatype_mappings = self.link_functions_with_datatype("mutations")
            self._check_function_type()
        elif mutation_datatype_file_path != None:
            f = open(mutation_datatype_file_path, 'r')
            self.mutation_datatype_mappings = json.load(f)
            f.close()
        if function_list_file_path != None:
            f = open(function_list_file_path, 'r')
            data = f.readlines()
            self.update_function_list(data)
            f.close()


    def update_function_list(self, newList):
        for line in newList:
            if line != "\n":
                args = line.split('\t')
                self.mutation_datatype_mappings[args[0]]['functionType'] = args[1].strip()
        return

    # given current datatype and all previously processed datatype list, this function
    # is to return all functions with at least 1 input parameters associated with 
    # current datatype, and all other parameters must associated with current or previous
    # processed datatypes. This is to figure out which function to be added into the 
    # fuzzing list.
    def get_query_mapping_by_input_datatype(self, current_datatype = None, datatype_list = []):
        function_list = {}
        if current_datatype == None:
            # Sometimes we will need to get all functions that have independent input datas
            # such as scalar only type or no input. In this case we will return all functions
            # without any datatype dependency. Note that this can be true independent function,
            # or because of failed to check datatype dependency for the input names.
            for function_name, function_body in self.mutation_datatype_mappings.items():
                checker = True
                if function_body["inputDatatype"] != None:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if input_body != None:
                            checker = False
                if checker:
                    function_list[function_name] = function_body
        else:
            # this is to add the current datatype to the datatype list for the 2nd loop
            datatype_list.append(current_datatype)
            for function_name, function_body in self.query_datatype_mappings.items():
                checker = False
                # In this first loop we are focusing on finding at lease 1 parameter
                # directly associated with the current datatype. This can filter out
                # previously processed functions and make sure all selected function 
                # have direct relationship with the current datatype.
                if function_body["inputDatatype"] != None:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if input_body == current_datatype:
                            checker = True
                # Then the 2nd loop is to filter out those parameters depending on datatypes
                # that are not yet processed. These functions will be called at a later 
                # time since every parameter will eventually being processed when there's 
                # enough datatypes in the processed datatype list.
                if checker:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if (input_body not in datatype_list) and input_body != None:
                            checker = False
                if checker:
                    function_list[function_name] = function_body
        return function_list


    # given current datatype and all previously processed datatype list, this function
    # is to return all functions with at least 1 input parameters associated with 
    # current datatype, and all other parameters must associated with current or previous
    # processed datatypes. This is to figure out which function to be added into the 
    # fuzzing list.
    def get_mutation_mapping_by_input_datatype(self, current_datatype = None, datatype_list = []):
        function_list = {}
        if current_datatype == None:
            # Sometimes we will need to get all functions that have independent input datas
            # such as scalar only type or no input. In this case we will return all functions
            # without any datatype dependency. Note that this can be true independent function,
            # or because of failed to check datatype dependency for the input names.
            for function_name, function_body in self.mutation_datatype_mappings.items():
                checker = True
                if function_body["inputDatatype"] != None:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if input_body != None:
                            checker = False
                if checker:
                    function_list[function_name] = function_body
        else:
            # this is to add the current datatype to the datatype list for the 2nd loop
            datatype_list.append(current_datatype)
            for function_name, function_body in self.mutation_datatype_mappings.items():
                checker = False
                # In this first loop we are focusing on finding at lease 1 parameter
                # directly associated with the current datatype. This can filter out
                # previously processed functions and make sure all selected function 
                # have direct relationship with the current datatype.
                if function_body["inputDatatype"] != None:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if input_body == current_datatype:
                            checker = True
                # Then the 2nd loop is to filter out those parameters depending on datatypes
                # that are not yet processed. These functions will be called at a later 
                # time since every parameter will eventually being processed when there's 
                # enough datatypes in the processed datatype list.
                if checker:
                    for input_name, input_body in function_body["inputDatatype"].items():
                        if (input_body not in datatype_list) and input_body != None:
                            checker = False
                if checker:
                    function_list[function_name] = function_body
        return function_list



    # given current datatype, this function is to return all functions with matched 
    # output datatype. Since there can be only 1 output datatype, there's no need 
    # to check previous processed datatypes.
    def get_query_mapping_by_output_datatype(self, current_datatype, explicit = False):
        function_list = {}
        for function_name, function_body in self.query_datatype_mappings.items():
            if function_body["outputDatatype"]["name"] == current_datatype:
                function_list[function_name] = function_body
            # If no direct connection, we have to search inside the output object for inner objects
            # Specify explicit to true to limit results with nonNull only
            elif self._search_function_output_datatype_recursive(current_datatype, function_body["outputDatatype"]["name"], explicit):
                function_list[function_name] = function_body
        return function_list


    # given current datatype, this function is to return all functions with matched 
    # output datatype. Since there can be only 1 output datatype, there's no need 
    # to check previous processed datatypes.
    def get_mutation_mapping_by_output_datatype(self, current_datatype, explicit = False):
        function_list = {}
        for function_name, function_body in self.mutation_datatype_mappings.items():
            if function_body["outputDatatype"]["name"] == current_datatype:
                function_list[function_name] = function_body
            # If no direct connection, we have to search inside the output object for inner objects
            # Specify explicit to true to limit results with nonNull only
            elif self._search_function_output_datatype_recursive(current_datatype, function_body["outputDatatype"]["name"], explicit):
                function_list[function_name] = function_body
                
        return function_list



    def _search_function_output_datatype_recursive(self, current_datatype, output_datatype, explicit = False):
        output_objects = self.objects
        # if 2 datatypes are matched, we return true immediately
        if current_datatype == output_datatype:
            return True
        else:
            # else we search recursively for each objects inside the output datatype
            # If explicit has been set to true we will only check for those objects 
            # with nonNull value.
            for arg_name, arg_body in output_objects[output_datatype]["fields"].items():
                arg_body = self._get_type(arg_body)
                if arg_body["kind"] == "OBJECT" and (not explicit or arg_body.get("nonNull") != None):
                    return self._search_function_output_datatype_recursive(current_datatype, arg_body["name"])

        return False


    def get_query_mappings(self):
        return self.query_datatype_mappings

    def get_mutation_mappings(self):
        return self.mutation_datatype_mappings

    def get_query_mapping(self, query_name):
        return self.query_datatype_mappings[query_name]

    def get_mutation_mapping(self, mutation_name):
        return self.mutation_datatype_mappings[mutation_name]

    def print_function_list(self, path):
        f = open(path, 'w')
        for function_name, function_body in self.mutation_datatype_mappings.items():
            f.writelines(function_name + "\t" + function_body['functionType'] + "\n")
        f.close()
        return


    def print_mutation_datatype_list(self, path):
        f = open(path, 'w')
        json.dump(self.mutation_datatype_mappings, f)
        f.close()
        return

    def print_query_datatype_list(self, path):
        f = open(path, 'w')
        json.dump(self.query_datatype_mappings, f)
        f.close()
        return

    def _check_function_type(self):
        function_objects = self.schema_json["mutations"]

        for function_name, function_body in function_objects.items():
            if re.search('[cC]reate|[aA]dd',function_name):
                self.mutation_datatype_mappings[function_name]["functionType"] = "Create"
            elif re.search('[dD]elete|[rR]emove',function_name):
                self.mutation_datatype_mappings[function_name]["functionType"] = "Delete"
            elif re.search('[uU]pdate',function_name):
                self.mutation_datatype_mappings[function_name]["functionType"] = "Update"
            else:
                self.mutation_datatype_mappings[function_name]["functionType"] = "Unknown"
        
        return



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

                # First we check if the function has input
                if function_body["args"] != None:
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
                else:
                    list[function_name]["inputDatatype"] = None

            elif output_data_type["kind"] == "SCALAR":
                list[function_name] = {}
                # here I just copy the raw data just in case
                list[function_name]["rawdata"] = function_body
                list[function_name]["inputDatatype"] = {}

                # since the output will be a single Object, we just copy its original structure here
                list[function_name]["outputDatatype"] = output_data_type

                # First we check if the function has input
                if function_body["args"] != None:
                    # then we check for any input items and see if it match any of the Objects
                    for arg_name, arg_body in function_body["args"].items():
                        # again we only focus on the real Object, not the status like LIST or something
                        arg_data_type = self._get_type(arg_body)
                        # if the scalar type is ID and the output is scalar, there's no way to find
                        # the related datatype. Thus we will just put a None for now. 
                        if arg_data_type["kind"] == "SCALAR" and arg_data_type["name"] == "ID":
                            list[function_name]["inputDatatype"][arg_name] = None
                        # if it is other scalar or enum type we will search the scalar-datatype list
                        # to look for matching names.
                        elif arg_data_type["kind"] == "SCALAR" or arg_data_type["kind"] == "ENUM":
                            list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                        # Similar as the input object type, even if there's an ID inside of it,
                        # we are unable to check for the related datatype. Thus we will put a None
                        # in here as well.
                        elif arg_data_type["kind"] == "INPUT_OBJECT":
                            list[function_name]["inputDatatype"][arg_name] = None
                else:
                    list[function_name]["inputDatatype"] = None

            elif output_data_type["kind"] == "INTERFACE":
                pass
            elif output_data_type["kind"] == "UNION":
                list[function_name] = {}
                # here I just copy the raw data just in case
                list[function_name]["rawdata"] = function_body
                list[function_name]["inputDatatype"] = {}

                # since the output will be a single Object, we just copy its original structure here
                list[function_name]["outputDatatype"] = output_data_type

                # First we check if the function has input
                if function_body["args"] != None:
                    # then we check for any input items and see if it match any of the Objects
                    for arg_name, arg_body in function_body["args"].items():
                        # again we only focus on the real Object, not the status like LIST or something
                        arg_data_type = self._get_type(arg_body)
                        # if the scalar type is ID and the output is scalar, there's no way to find
                        # the related datatype. Thus we will just put a None for now. 
                        if arg_data_type["kind"] == "SCALAR" and arg_data_type["name"] == "ID":
                            list[function_name]["inputDatatype"][arg_name] = None
                        # if it is other scalar or enum type we will search the scalar-datatype list
                        # to look for matching names.
                        elif arg_data_type["kind"] == "SCALAR" or arg_data_type["kind"] == "ENUM":
                            list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                        # Similar as the input object type, even if there's an ID inside of it,
                        # we are unable to check for the related datatype. Thus we will put a None
                        # in here as well.
                        elif arg_data_type["kind"] == "INPUT_OBJECT":
                            list[function_name]["inputDatatype"][arg_name] = None
                else:
                    list[function_name]["inputDatatype"] = None


            elif output_data_type["kind"] == "ENUM":
                pass
            # This should be impossible, but we just put it here just in case.
            # elif output_data_type["kind"] == "INPUT_OBJECT":
            #    pass

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



f = open("shopify_compiled.json", 'r')
#f = open("compiled_schema2.json", "r")
objects = json.load(f)

test = FunctionBuilder(objects)
test1 = test.get_query_mappings()
test2 = test.get_mutation_mappings()
test4 = test.get_query_mapping_by_input_datatype("MailingAddress")
test5 = test.get_query_mapping_by_output_datatype("MailingAddress")
test6 = test.get_mutation_mapping_by_input_datatype("MailingAddress")
test7 = test.get_mutation_mapping_by_output_datatype("MailingAddress")
##test5 = test.get_mutation_mapping("checkoutCompleteFree")
test.print_function_list('function_list.txt')
test3 = ""

