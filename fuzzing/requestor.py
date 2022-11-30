import sys, os, random
from request.request import Request

def is_dynamic_parameter(arg):
    return arg["kind"] == "SCALAR" and arg["name"] == 'ID'

class Requestor:
    def __init__(self, req_seq, cache, fuzzer, url):
        self.req_seq = req_seq
        self.cache = cache
        self.current_request = req_seq[0]
        self.fuzzer = fuzzer
        self.url = url

    def concretize(self):
        current_request = self.current_request
        prepared_payload = self.fuzzer.concretize_payload(current_request.prepare_payload())
        

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
