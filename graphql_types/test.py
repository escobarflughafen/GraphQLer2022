

fields = {
    'A': True,
    'B': {
        'X': True,
        'Y': {
            'name': True,
            'address': True
        }
    },
    'C': {
        'U': True
    }

}



def request(name, url, fields, **args):

    name_fragment =         f'''{name}'''
        
    def parse_arg_type(arg):
        if isinstance(arg, str):
            return f'"{arg}"'
        
        else:
            return arg
            


    args_fragment =         f'''({', '.join(
                                    [f'{arg}: {parse_arg_type(args[arg])}' for arg in args]
                                )})'''
        
    def parse_fields(fields):
        string = '{'

        for field in fields:
            if fields[field] == True:
                string += field + '\n'
        
            else:
                string += parse_fields(fields[field])
            
        string += '}'

        return string

    response_fragment =     parse_fields(fields)

    query = name_fragment + ' ' + args_fragment + ' ' + response_fragment

    # query = f'''
    # {self.name} (f"({','.join([f"{arg}: {args[arg]}" for arg in args])})" if args else "") {{
    # {'\n'.join(fields)}
    # }}
    # '''

    # return query
    print(query)

    return query

request('test', 'test.url', fields, username="abc", password="1234")
