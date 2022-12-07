import argparse
import os
import introspection.parse as parse
import json
from request import request
from pprint import pprint
from fuzzing.requestor import Requestor
from fuzzing.cache import Cache
from fuzzing.fuzzer.constant import ConstantFuzzer
import yaml
from fuzzing.process_functions import FunctionBuilder


def get_args():
    parser = argparse.ArgumentParser(
        '''
        GraphQLer - a stateful fuzzing tool on GraphQL
        '''
    )

    parser.add_argument(
        '--mode', '-mode',
        required=True,
        type=str,
        choices=["compile", "fuzz", "debug", "debug_fuzzing"],
        default="compile"
    )

    parser.add_argument(
        '--test', '-t',
        action='store_true'
    )

    parser.add_argument(
        '--url', '-u',
        type=str
    )

    parser.add_argument(
        '--wordlist', '-w',
        type=str
    )

    parser.add_argument(
        '--introspection-json', '-i',
        type=str
    )

    parser.add_argument(
        '--save', '-o',
        type=str
    )

    parser.add_argument(
        '--schema',
        type=str
    )

    # parser.add_argument(
    #'--wordlist-dir', '-w',
    # type=str
    # )

    # parser.add_argument(

    # )

    return parser


if __name__ == '__main__':
    args = get_args().parse_args()
    test = args.test
    if test:
        print(args)

    if args.mode == "compile":
        url = args.url
        introspection_json_path = args.introspection_json
        if url:
            schema_builder = parse.SchemaBuilder(url=url)
        elif introspection_json_path:
            with open(introspection_json_path) as f:
                schema_builder = parse.SchemaBuilder(
                    introspection_json=json.load(f))
        else:
            raise Exception(
                "please add corrent introspection source to arguments by --url or --introspection-json")

        print(schema_builder.prepared_schema)

        if args.save:
            schema_builder.dump(path=args.save)
        else:
            schema_builder.dump()

        function_builder = FunctionBuilder(args.save)

        function_builder.generate_grammer_file()

    elif args.mode == 'fuzz':
        url = args.url

    elif args.mode == 'debug':
        url = args.url
        introspection_json_path = args.introspection_json
        if url:
            schema_builder = parse.SchemaBuilder(url=url)
        elif introspection_json_path:
            with open(introspection_json_path) as f:
                schema_builder = parse.SchemaBuilder(
                    introspection_json=json.load(f))
        else:
            raise Exception(
                "please add corrent introspection source to arguments by --url or --introspection-json")

        pprint(schema_builder.prepared_schema)
        selected_query = schema_builder.prepared_schema["queries"]["getTransaction"]
        selected_query.prepare_payload(schema_builder.schema)
        print(selected_query.stringify_payload(
            selected_query.prepared_payload))

        pprint(selected_query.prepared_payload)

        request = request.Request(url, request.Request.MODE_QUERY)
        request.add_payload(selected_query.stringify_payload(
            selected_query.prepared_payload))

        print(request.get_request_body())
        print(request.request())

    elif args.mode == 'debug_fuzzing':
        url = args.url
        introspection_json_path = args.introspection_json
        parsed_schema_path = args.schema

        schema_file_name = 'schema.json'
        function_list_file_name = 'function_list.txt'
        query_parameter_file_name = 'query_parameter.txt'
        mutation_parameter_file_name = 'mutation_parameter.txt'

        if parsed_schema_path:
            with open(os.path.join(parsed_schema_path, schema_file_name)) as f:
                schema = json.load(f)
        elif url:
            schema_builder = parse.SchemaBuilder(url=url)
        elif introspection_json_path:
            with open(introspection_json_path) as f:
                schema_builder = parse.SchemaBuilder(
                    introspection_json=json.load(f))
        else:
            raise Exception(
                "please add corrent introspection source to arguments by --url or --introspection-json")

        function_builder = FunctionBuilder(
            os.path.join(parsed_schema_path, schema_file_name),
            query_parameter_file_path=os.path.join(parsed_schema_path, query_parameter_file_name),
            mutation_parameter_file_path=os.path.join(parsed_schema_path, mutation_parameter_file_name)
        )

        req_seq = [
            'createUser',
            'getUser',
            'updateUser',
            'createCurrency',
            'createWallet',
            'getCurrency',
            'updateCurrency',
            'createLocation',
            'getLocation',
            'updateLocation',
            'createWallet',
            'getWallet',
            'updateWallet',
            'createTransaction',
            'getTransaction',
            'updateTransaction',
            'deleteTransaction',
            'deleteWallet',
            'deleteLocation',
            'deleteCurrency',
            'deleteUser',
        ]

        cache = Cache(schema)
        function_builder = FunctionBuilder(parsed_schema_path, )
        requestor = Requestor(req_seq,
                              cache,
                              ConstantFuzzer(schema, cache),
                              url,
                              schema,
                        )

        requestor.execute(schema)
