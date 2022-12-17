import json
import re
import yaml
import os
import pprint


class FunctionBuilder:
    """
    The class for 'function - input/output - datatype_object' mapping.

    Attributes
    ----------
    schema_json_file_path: the processed schema json file to be imported. This is mandatory.
    function_list_file_path: the 'function - function_type' mapping file to be imported. If the file is provided, the 'function - function_type' mapping will be updated based on the file.
    query_parameter_file_path: the 'input/output - datatype_object' mapping for query functions. If the file is provided, the 'input/output - datatype_object' mapping will be updated based on the file.
    mutation_parameter_file_path: the 'input/output - datatype_object' mapping for mutation functions. If the file is provided, the 'input/output - datatype_object' mapping will be updated based on the file.

    Methods
    -------
    get_query_mapping_by_input_datatype(self, current_datatype = None, datatype_list = [])
        Return all query functions with at least 1 input parameters associated with current datatype and meet all dependency requirements.
    get_mutation_mapping_by_input_datatype(self, current_datatype = None, datatype_list = [])
        Return all mutation functions with at least 1 input parameters associated with current datatype and meet all dependency requirements.
    get_query_mapping_by_output_datatype(self, current_datatype, explicit = False):
        Return all query functions with output object associated with current datatype and meet all dependency requirements.
    get_mutation_mapping_by_output_datatype(self, current_datatype, explicit = False):
        Return all mutation functions with output object associated with current datatype and meet all dependency requirements.
    """

    # during the first call, usually we only provide schema json file and there will be 3 files generated for user to fix
    # next call we will load original schema with 3 modified files and the datatype will be overwrited during the initialication
    def __init__(self, schema_json_file_path, function_list_file_path = None, query_parameter_file_path = None, mutation_parameter_file_path = None, perform_scalar_datatype_mapping = True):
        """
        Parameters
        ----------
        schema_json_file_path: the processed schema json file to be imported. This is mandatory.
        function_list_file_path: the 'function - function_type' mapping file to be imported. If the file is provided, the 'function - function_type' mapping will be updated based on the file.
        query_parameter_file_path: the 'input/output - datatype_object' mapping for query functions. If the file is provided, the 'input/output - datatype_object' mapping will be updated based on the file.
        mutation_parameter_file_path: the 'input/output - datatype_object' mapping for mutation functions. If the file is provided, the 'input/output - datatype_object' mapping will be updated based on the file.
        """
        f = open(schema_json_file_path, "r")
        schema_json = json.load(f)
        f.close()
        self.schema_json = schema_json
        self.objects = schema_json["objects"]
        self.perform_scalar_datatype_mapping = perform_scalar_datatype_mapping

        # if there are no input type, we won't load input object list
        if schema_json.get("inputObjects") != None:
            self.input_objects = schema_json["inputObjects"]

        # if there are no queries, we will not proceed to build query list
        if schema_json.get("queries") != None:
            self.queries = schema_json["queries"]
            self.query_datatype_mappings = self.link_functions_with_datatype("queries")
        
        # if there are no motations, we will not proceed to build mutation list
        if schema_json.get("mutations") != None:
            self.mutations = schema_json["mutations"]
            self.mutation_datatype_mappings = self.link_functions_with_datatype("mutations")
            self._check_function_type()
        
        # if the function list file is provided, we will use the user input to overwrite the original result
        if function_list_file_path != None:
            self.update_function_type(function_list_file_path)

        # if the query parameter datatype list file is provided, we will use the user input to overwrite the original result
        if query_parameter_file_path != None:
            self.read_query_parameter_list(query_parameter_file_path)

        # if the mutation parameter datatype list file is provided, we will use the user input to overwrite the original result
        if mutation_parameter_file_path != None:
            self.read_mutation_parameter_list(mutation_parameter_file_path)


    # given current datatype and all previously processed datatype list, this function
    # is to return all functions with at least 1 input parameters associated with 
    # current datatype, and all other parameters must associated with current or previous
    # processed datatypes. This is to figure out which function to be added into the 
    # fuzzing list.

    def get_query_mapping_by_input_datatype(self, current_datatype = None, datatype_list = []):
        """
        Return all query functions with at least 1 input parameters associated with current datatype and meet all dependency requirements.

        Parameters
        ----------
        current_datatype: current datatype to be mapped with. 'None' by default and it will return all functions with independent input.
        datatype_list: previous datatype list for which are already processed. It will not return any function name with any dependent datatype for any variable not found in this list.
        """
        function_list = {}
        # we check for each functions in the query function list
        for function_name, function_body in self.query_datatype_mappings.items():
            # if function_body["inputDatatype"] is None, it usually means that the function does not need any input and it is fully independent. Thus we will just output the function name directly.
            if function_body["inputDatatype"] != None:
                # else we have to add the current datatype to the list first.
                datatype_list.append(current_datatype)
                # we will then recursively search for dependency 
                checker = self._get_inner_mapping_by_input_datatype(current_datatype, datatype_list, function_body["inputDatatype"])
                if checker:
                    function_list[function_name] = function_body
            else:
                function_list[function_name] = function_body
        return function_list


    # Search in the input and check for dependency. For input objects it will expand it and search recursively.
    def _get_inner_mapping_by_input_datatype(self, current_datatype, datatype_list, datatype_mapping_json):
        if current_datatype == None:
            checker = True
            for input_name, input_body in datatype_mapping_json.items():
                if isinstance(input_body, dict):
                    checker = self._get_inner_mapping_by_input_datatype(current_datatype, datatype_list, input_body)
                else:
                    if input_body != None:
                        checker = False
        else:
            checker = False
            for input_name, input_body in datatype_mapping_json.items():
                if (not isinstance(input_body, dict)) and input_body == current_datatype:
                    checker = True
            if checker:
                for input_name, input_body in datatype_mapping_json.items():
                    if isinstance(input_body, dict):
                        checker = self._get_inner_mapping_by_input_datatype(current_datatype, datatype_list, input_body)
                if checker:
                    for input_name, input_body in datatype_mapping_json.items():
                        if (not isinstance(input_body, dict)) and (input_body not in datatype_list) and input_body != None:
                            checker = False
            return checker
                    



    # given current datatype and all previously processed datatype list, this function
    # is to return all functions with at least 1 input parameters associated with 
    # current datatype, and all other parameters must associated with current or previous
    # processed datatypes. This is to figure out which function to be added into the 
    # fuzzing list.
    def get_mutation_mapping_by_input_datatype(self, current_datatype = None, datatype_list = []):
        """
        Return all mutation functions with at least 1 input parameters associated with current datatype and meet all dependency requirements.

        Parameters
        ----------
        current_datatype: current datatype to be mapped with. 'None' by default and it will return all functions with independent input.
        datatype_list: previous datatype list for which are already processed. It will not return any function name with any dependent datatype for any variable not found in this list.
        """
        function_list = {}
        for function_name, function_body in self.mutation_datatype_mappings.items():
            if function_body["inputDatatype"] != None:
                datatype_list.append(current_datatype)
                checker = self._get_inner_mapping_by_input_datatype(current_datatype, datatype_list, function_body["inputDatatype"])
                if checker:
                    function_list[function_name] = function_body
            else:
                function_list[function_name] = function_body
        return function_list


    # given current datatype, this function is to return all functions with matched 
    # output datatype. Since there can be only 1 output datatype, there's no need 
    # to check previous processed datatypes.
    def get_query_mapping_by_output_datatype(self, current_datatype, explicit = False):
        """
        Return all query functions with output object associated with current datatype and meet all dependency requirements.

        Parameters
        ----------
        current_datatype: current datatype to be mapped with. 'None' by default and it will return all functions with independent input.
        explicit: If this set to True, it will check every child object even without 'nonNull' parameter. It is 'False' by default to only check for 'nonNull' child objects.
        """
        function_list = {}
        for function_name, function_body in self.query_datatype_mappings.items():
            if function_body["outputDatatype"]["name"] == current_datatype:
                function_list[function_name] = function_body
            # If no direct connection, we have to search inside the output object for inner objects
            # Specify explicit to true to limit results with nonNull only
            elif function_body["outputDatatype"]["kind"] == "OBJECT" and self._search_function_output_datatype_recursive(current_datatype, function_body["outputDatatype"]["name"], explicit):
                function_list[function_name] = function_body
        return function_list


    # given current datatype, this function is to return all functions with matched 
    # output datatype. Since there can be only 1 output datatype, there's no need 
    # to check previous processed datatypes.
    def get_mutation_mapping_by_output_datatype(self, current_datatype, explicit = False):
        """
        Return all mutation functions with output object associated with current datatype and meet all dependency requirements.

        Parameters
        ----------
        current_datatype: current datatype to be mapped with. 'None' by default and it will return all functions with independent input.
        explicit: If this set to True, it will check every child object even without 'nonNull' parameter. It is 'False' by default to only check for 'nonNull' child objects.
        """
        function_list = {}
        for function_name, function_body in self.mutation_datatype_mappings.items():
            if function_body["outputDatatype"]["name"] == current_datatype:
                function_list[function_name] = function_body
            # If no direct connection, we have to search inside the output object for inner objects
            # Specify explicit to true to limit results with nonNull only
            elif function_body["outputDatatype"]["kind"] == "OBJECT" and self._search_function_output_datatype_recursive(current_datatype, function_body["outputDatatype"]["name"], explicit):
                function_list[function_name] = function_body
                
        return function_list



    def _search_function_output_datatype_recursive(self, current_datatype, output_datatype, explicit = False, past_datatype = []):
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
                if arg_body["kind"] == "OBJECT" and (not explicit or arg_body.get("nonNull") != None) and (arg_body["name"] not in past_datatype):
                    past_datatype.append(output_datatype)
                    return self._search_function_output_datatype_recursive(current_datatype, arg_body["name"], explicit, past_datatype)

        return False


    def get_query_mappings(self):
        return self.query_datatype_mappings

    def get_mutation_mappings(self):
        return self.mutation_datatype_mappings

    def get_query_mapping(self, query_name):
        return self.query_datatype_mappings[query_name]

    def get_mutation_mapping(self, mutation_name):
        return self.mutation_datatype_mappings[mutation_name]

    # generate a file with automatically generated function type to let user modify later
    def print_function_list(self, path):
        """
        !for debug only, please call 'generate_grammar_file' for production
        Generate 'function - function_type' mapping file.

        Parameters
        ----------
        path: location and name to save the file to.
        """
        f = open(path, 'w')
        output_json = {}
        for function_name, function_body in self.mutation_datatype_mappings.items():
            output_json[function_name] = function_body["functionType"]
        f.write(yaml.dump(output_json))
        f.close()
        return

    # generate a file with generated parameter type for query types to let user modify later
    def print_query_parameter_list(self, path):
        """
        !for debug only, please call 'generate_grammar_file' for production
        Generate 'input/output - datatype_object' mapping file for query functions.

        Parameters
        ----------
        path: location and name to save the file to.
        """
        f = open(path, 'w')
        output_json = {}
        for function_name, function_body in self.query_datatype_mappings.items():
            output_json[function_name] = {}
            output_json[function_name]["input"] = {}
            if function_body["inputDatatype"] != None:
                for input_name, input_dependency_object_name in function_body["inputDatatype"].items():
                    output_json[function_name]["input"][input_name] = input_dependency_object_name
            else:
                output_json[function_name]["input"] = None
            output_json[function_name]["output"] = function_body["outputDatatype"]
        f.write(yaml.dump(output_json))
        f.close()
        return

    # generate a file with generated parameter type for mutation types to let user modify later
    def print_mutation_parameter_list(self, path):
        """
        !for debug only, please call 'generate_grammar_file' for production
        Generate 'input/output - datatype_object' mapping file for mutation functions.

        Parameters
        ----------
        path: location and name to save the file to.
        """
        f = open(path, 'w')
        output_json = {}
        for function_name, function_body in self.mutation_datatype_mappings.items():
            output_json[function_name] = {}
            output_json[function_name]["input"] = {}
            if function_body["inputDatatype"] != None:
                for input_name, input_dependency_object_name in function_body["inputDatatype"].items():
                    output_json[function_name]["input"][input_name] = input_dependency_object_name
            else:
                output_json[function_name]["input"] = None
            output_json[function_name]["output"] = function_body["outputDatatype"]
        f.write(yaml.dump(output_json))
        f.close()
        return

    # combined function for the process control. Generate 1-3 files depending on the existance of quiries and mutations
    def generate_grammar_file(self, path):
        """
        Generate grammar file for user to modify if needed.
        It will generate 1-3 yaml files based on the existance of query and mutation group of the GraphQL API.
        mutation_function_list.yml: 'function - function_type' mapping file for mutation functions.
        query_parameter_list.yml: 'input/output - datatype_object' mapping file for query functions.
        mutation_parameter_list.yml: 'input/output - datatype_object' mapping file for mutation functions.

        Parameters
        ----------
        path: location to save the file to. The file name is fixed and no need to specify.
        """
        if self.schema_json.get("queries") != None:
            self.print_query_parameter_list(os.path.join(path, "query_parameter_list.yml"))
        if self.schema_json.get("mutations") != None:
            self.print_function_list(os.path.join(path, "mutation_function_list.yml"))
            self.print_mutation_parameter_list(os.path.join(path, "mutation_parameter_list.yml"))


    # update function type based on user modified yaml file
    def update_function_type(self, path):
        """
        Read the 'function - function_type' mapping file and update schema based on the file.

        Parameters
        ----------
        path: location and name to read the file from.
        """
        f = open(path, 'r')
        input_json = yaml.load(f.read())
        for function_name, function_type in input_json.items():
                self.mutation_datatype_mappings[function_name]["functionType"] = function_type
        return

    # load the query parameter file and update existing schema to match user input
    def read_query_parameter_list(self, path):
        """
        Read the 'input/output - datatype_object' mapping file for query functions and update schema based on the file.

        Parameters
        ----------
        path: location and name to read the file from.
        """
        f = open(path, 'r')
        input_json = yaml.load(f.read())
        for function_name, function_body in input_json.items():
            self.query_datatype_mappings[function_name]["inputDatatype"] = function_body["input"]
            self.query_datatype_mappings[function_name]["outputDatatype"] = function_body["output"]
        f.close()
        return
    
    # load the mutation parameter file and update existing schema to match user input
    def read_mutation_parameter_list(self, path):
        """
        Read the 'input/output - datatype_object' mapping file for mutation functions and update schema based on the file.

        Parameters
        ----------
        path: location and name to read the file from.
        """
        f = open(path, 'r')
        input_json = yaml.load(f.read())
        for function_name, function_body in input_json.items():
            self.mutation_datatype_mappings[function_name]["inputDatatype"] = function_body["input"]
            self.mutation_datatype_mappings[function_name]["outputDatatype"] = function_body["output"]
        f.close()
        return

    # given function type and function name, this function returns the json structure with ofDatatype parameter for the use of function call later
    def build_function_call_schema(self, function_type, function_name):
        output_json = {}
        if function_type == "query":
            output_json[function_name] = self.query_datatype_mappings[function_name]["rawdata"]
            output_json[function_name]["type"]["ofDatatype"] = self.query_datatype_mappings[function_name]["outputDatatype"]["name"]
            if self.query_datatype_mappings[function_name]["rawdata"]["args"] != None:
                for arg_name, arg_body in self.query_datatype_mappings[function_name]["rawdata"]["args"].items():
                    if arg_body["kind"] == "INPUT_OBJECT":
                        output_json[function_name]["args"][arg_name]["args"] = self._build_inner_input_datatype_call_schema(arg_body["name"], self.query_datatype_mappings[function_name]["inputDatatype"][arg_name])
                    else:
                        output_json[function_name]["args"][arg_name]["ofDatatype"] = self.query_datatype_mappings[function_name]["inputDatatype"][arg_name]
            else:
                output_json[function_name]["args"] = {}
        elif function_type == "mutation":
            output_json[function_name] = self.mutation_datatype_mappings[function_name]["rawdata"]
            output_json[function_name]["functionType"] = self.mutation_datatype_mappings[function_name]["functionType"]
            output_json[function_name]["type"]["ofDatatype"] = self.mutation_datatype_mappings[function_name]["outputDatatype"]["name"]
            if self.mutation_datatype_mappings[function_name]["rawdata"]["args"] != None:
                for arg_name, arg_body in self.mutation_datatype_mappings[function_name]["rawdata"]["args"].items():
                    if arg_body["kind"] == "INPUT_OBJECT":
                        output_json[function_name]["args"][arg_name]["args"] = self._build_inner_input_datatype_call_schema(arg_body["name"], self.mutation_datatype_mappings[function_name]["inputDatatype"][arg_name])
                    else:
                        output_json[function_name]["args"][arg_name]["ofDatatype"] = self.mutation_datatype_mappings[function_name]["inputDatatype"][arg_name]
            else:
                output_json[function_name]["args"] = {}
        return output_json


    def _build_inner_input_datatype_call_schema(self, input_object_name, datatype_mapping):
        output_json = self.input_objects[input_object_name]["fields"]
        for arg_name, arg_body in self.input_objects[input_object_name]["fields"].items():
            if arg_body["kind"] == "LIST":
                output_json[arg_name]["ofType"]["args"] = self._build_inner_input_datatype_call_schema(arg_body["ofType"]["name"], datatype_mapping[arg_name])
            if arg_body["kind"] == "INPUT_OBJECT":
                output_json[arg_name]["args"] = self._build_inner_input_datatype_call_schema(arg_body["name"], datatype_mapping[arg_name])
            else:
                output_json[arg_name]["ofDatatype"] = datatype_mapping[arg_name]
        return output_json



    # Estimate possible operation types by checking for key words in the function name
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


    # main function to map datatype with parameters in the query and mutations
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
                            if self.perform_scalar_datatype_mapping:
                                list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                            else:
                                list[function_name]["inputDatatype"][arg_name] = None
                        # Otherwise if it is an input object, we will expand and replace the input object with 
                        # the actual object inside it. We will also check if there's any ID type
                        # inside the input object. Then we are basically doing similar things by searching
                        # inside the output datatype and find the mapping.
                        elif arg_data_type["kind"] == "INPUT_OBJECT":
                            list[function_name]["inputDatatype"][arg_name] = self._expand_object_from_input_object(arg_data_type["name"], output_data_type["name"])
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
                            if self.perform_scalar_datatype_mapping:
                                list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                            else:
                                list[function_name]["inputDatatype"][arg_name] = None
                        # Otherwise if it is an input object, we will expand and replace the input object with 
                        # the actual object inside it. We will also check if there's any ID type
                        # inside the input object. Then we are basically doing similar things by searching
                        # inside the output datatype and find the mapping.
                        elif arg_data_type["kind"] == "INPUT_OBJECT":
                            list[function_name]["inputDatatype"][arg_name] = self._expand_object_from_input_object(arg_data_type["name"], None)
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
                            if self.perform_scalar_datatype_mapping:
                                list[function_name]["inputDatatype"][arg_name] = self._get_scalar_with_datatype(arg_name)
                            else:
                                list[function_name]["inputDatatype"][arg_name] = None
                        # Otherwise if it is an input object, we will expand and replace the input object with 
                        # the actual object inside it. We will also check if there's any ID type
                        # inside the input object. Then we are basically doing similar things by searching
                        # inside the output datatype and find the mapping.
                        elif arg_data_type["kind"] == "INPUT_OBJECT":
                            list[function_name]["inputDatatype"][arg_name] = self._expand_object_from_input_object(arg_data_type["name"], None)
                else:
                    list[function_name]["inputDatatype"] = None


            elif output_data_type["kind"] == "ENUM":
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

    # check input object and expand it to datatype mappings
    # if any ID type exists, it will check the output object for any ID type and mapping the datatype with the input
    def _expand_object_from_input_object(self, input_object_datatype, output_datatype):
        input_objects = self.input_objects
        output = {}

        # we check for every object inside the input object and see if it is an ID type
        for input_object_name, input_object_body in input_objects[input_object_datatype]["fields"].items():
            input_object_body = self._get_type(input_object_body)
            if input_object_body["kind"] == "SCALAR" and input_object_body["name"] == "ID":
                if output_datatype == None:
                    output[input_object_name] = None
                else:
                    output[input_object_name] = self._search_related_object(input_object_name, output_datatype)
            # if it is other scalar or enum type we will search the scalar-datatype list
            # to look for matching names.
            elif input_object_body["kind"] == "SCALAR" or input_object_body["kind"] == "ENUM":
                if self.perform_scalar_datatype_mapping:
                    output[input_object_name] = self._get_scalar_with_datatype(input_object_name)
                else:
                    output[input_object_name] = None
            # if we found an inner object, we call the function again to search for the input object name recursively
            elif input_object_body["kind"] == "INPUT_OBJECT":
                output[input_object_name] = self._expand_object_from_input_object(input_object_body["name"], output_datatype)
            else:
                output[input_object_name] = None
        return output


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


#test = FunctionBuilder("debug/schema.json")

#test.generate_grammar_file()
#test2 = test.build_function_call_schema("mutation", "checkoutAttributesUpdate")

#print(test2)
'''
test = FunctionBuilder("schema_wallet.json", query_parameter_file_path="function_input.txt", mutation_parameter_file_path="function_mutation_input.txt")
test1 = test.get_query_mappings()
test2 = test.get_mutation_mappings()

test4 = test.get_query_mapping_by_input_datatype("Message")
test5 = test.get_query_mapping_by_output_datatype("Message")
test6 = test.get_mutation_mapping_by_input_datatype("Message")
test7 = test.get_mutation_mapping_by_output_datatype("Message")
test.print_function_list('function_list.txt')
test8 = test.build_function_call_schema("mutation", "createUser")
test.print_query_parameter_list('function_input.txt')
#test.read_query_parameter_list('function_input.txt')
test.print_mutation_parameter_list('function_mutation_input.txt')
#test.read_mutation_parameter_list('function_mutation_input.txt')
test3 = ""
'''
