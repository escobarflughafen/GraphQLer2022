from process_functions import FunctionBuilder
import json 
from pprint import pprint


class Requester:
    def __init__(self, SCHEMAFILE, OBJECTSEQFILE):
        # Read files.
        schema_file = open(SCHEMAFILE, "r")
        schema_json = json.load(schema_file)

        object_sequence_file = open(OBJECTSEQFILE, "r")
        self.object_sequence = json.load(object_sequence_file)["object_senquence"]

        self.fb = FunctionBuilder(schema_json, query_parameter_file_path="function_input.txt", mutation_parameter_file_path="function_mutation_input.txt")
        self.processed_objects = []
        self.request_sequence = []
        self.object_stack = []


    def function_checking(self, funcs, action, ob):
        '''
        Provide with a list of functions, checking if any object type exists as function input.
        Further check if we have created/processed those object type before.
        Update the request-sequence-list and processed-object-list correspondingly.
        '''
        if funcs:
            for f_name, f_body in funcs.items():
                # Mutation-Only: Filter function type.
                if action is not None:
                    if f_body.get("functionType") and f_body["functionType"].upper() != action:
                        continue

                if f_body["inputDatatype"]:
                    input_objects = f_body["inputDatatype"]
                    pass_checking = True
                    for in_name, in_type in input_objects.items():
                        # Further checking the object type.
                        if action == "CREATE" and (in_type in self.object_sequence) and (in_type not in self.processed_objects):
                            pass_checking = False
                            break
                    if pass_checking:
                        self.request_sequence.append(f_name)
                        self.processed_objects.append(ob)
                else:
                    self.request_sequence.append(f_name)
                    self.processed_objects.append(ob) 


    def build_request_sequence(self, OUTPUTFILE):
        for ob in self.object_sequence:
            # Add current object to the stack.
            self.object_stack.append(ob)

            # MUTATION: CREATE
            candidateFunc = self.fb.get_mutation_mapping_by_output_datatype(ob)
            self.function_checking(candidateFunc, "CREATE", ob)

            # QUERY: GET
            candidateFunc = self.fb.get_query_mapping_by_input_datatype(ob)
            self.function_checking(candidateFunc, None, ob)

            # MUTATION: UPDATE
            candidateFunc = self.fb.get_mutation_mapping_by_input_datatype(ob)
            self.function_checking(candidateFunc, "UPDATE", ob)
        
        while len(self.object_stack) > 0:
            ob = self.object_stack.pop()

            # MUTATION: DELETE
            candidateFunc = self.fb.get_mutation_mapping_by_input_datatype(ob)
            self.function_checking(candidateFunc, "DELETE", ob)

        self.generate_request_sequence(OUTPUTFILE)


    def generate_request_sequence(self, OUTPUTFILE):
        f = open(OUTPUTFILE, 'w')
        for x in self.request_sequence:
            f.writelines(x + "\n")
        f.close()

#f = open("shopify_compiled.json", "r")
#objects = json.load(f)

#test = FunctionBuilder(objects)
#test.print_query_datatype_list("query_datatype_mappings.json")
#test.print_mutation_datatype_list("mutation_datatype_mappings.json")

SCHEMAFILE = "schema_wallet.json"
OBJECTSEQFILE = "object_sequence.json"
r = Requester(SCHEMAFILE, OBJECTSEQFILE)
r.build_request_sequence("neogeek_request_sequence.txt")
#r.print_request_sequence()


#currFunc = fb.get_mutation_mapping_by_output_datatype(object_sequence[0])
#print("curr")
#pprint(object_sequence)
#pprint(currFunc)

'''

for ob in object_sequence:
    # MUTATION: CREATE
    candidateFunc = fb.get_mutation_mapping_by_output_datatype(ob)
    function_checking(candidateFunc, "CREATE")

    
    if candidateFunc:
        for f_name, f_body in candidateFunc.items():
            # Filter function type.
            if f_body["functionType"].upper() == "CREATE":
                if f_body["inputDatatype"]:
                    input_objects = f_body["inputDatatype"]
                    pass_checking = True
                    for in_name, in_type in input_objects.items():
                        # Further checking the object type.
                        if in_type in object_sequence:
                            if in_type not in processed_object_list:
                                pass_checking = False
                                break
                    if pass_checking:
                        # TODO: instead of adding function name, try send the request directly.
                        request_sequence.append(f_name)
                        processed_object_list.append(ob) # TODO: process object list check already exist
                else:
                    request_sequence.append(f_name)
                    processed_object_list.append(ob)
    

    # QUERY: GET
    candidateFunc = fb.get_query_mapping_by_output_datatype(ob)
    function_checking(candidateFunc, None)

    
    if candidateFunc:
        for f_name, f_body in candidateFunc.items():
            if f_body["inputDatatype"]:
                input_objects = f_body["inputDatatype"]
                pass_checking = True
                for in_name, in_type in input_objects.items():
                    # Further checking the object type.
                    if in_type in object_sequence:
                        if in_type not in processed_object_list:
                            pass_checking = False
                            break
                if pass_checking:
                    # TODO: instead of adding function name, try send the request directly.
                    request_sequence.append(f_name)
                    processed_object_list.append(ob)
            else:
                request_sequence.append(f_name)
                processed_object_list.append(ob)
    

    # MUTATION: UPDATE
    candidateFunc = fb.get_query_mapping_by_input_datatype(ob)
    function_checking(candidateFunc, "UPDATE")

    
    if candidateFunc:
        for f_name, f_body in candidateFunc.items():
            # Filter function type.
            if f_body["functionType"].upper() == "UPDATE":
                if f_body["inputDatatype"]:
                    input_objects = f_body["inputDatatype"]
                    pass_checking = True
                    for in_name, in_type in input_objects.items():
                        # Further checking the object type.
                        if in_type in object_sequence:
                            if in_type not in processed_object_list:
                                pass_checking = False
                                break
                    if pass_checking:
                        # TODO: instead of adding function name, try send the request directly.
                        request_sequence.append(f_name)
                        processed_object_list.append(ob) # TODO: process object list check already exist
                else:
                    request_sequence.append(f_name)
                    processed_object_list.append(ob)
''' 




'''

test = FunctionBuilder(objects)
test1 = test.get_query_mappings()
test2 = test.get_mutation_mappings()
test4 = test.get_query_mapping_by_input_datatype("LegacyCoupon", [])
test5 = test.get_query_mapping_by_output_datatype("LegacyCoupon")
test6 = test.get_mutation_mapping_by_input_datatype("LegacyCoupon", [])
test7 = test.get_mutation_mapping_by_output_datatype("LegacyCoupon")
##test5 = test.get_mutation_mapping("checkoutCompleteFree")
test.print_function_list('function_list.txt')
test3 = ""

'''