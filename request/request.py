from connect import connect

class Request:
    MODE_QUERY = "query"
    MODE_MUTATION = "mutation"
    modes = [MODE_QUERY, MODE_MUTATION]

    def __init__(self, url, mode, **args):
        if mode not in self.modes:
            raise Exception("unsupported GraphQL request mode")

        self.mode = mode
        self.sequence = []
        self.args = args
        self.url = url

    def get_request_body(self):
        body = ""

        body += self.mode 
        body += ' {\n'
        body += '\n'.join(self.sequence)
        body += '\n}'
        
        return body

    def request(self):
        request_body = self.get_request_body()
        return connect.send_request(self.url, request_body)
        
    def add_payload(self, req_payload):
        self.sequence.append(req_payload)