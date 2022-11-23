import argparse
import time
from os import error
import introspection.parse as parse
import json
from request import request
from pprint import pprint
from fuzzing import orchestrator
import logging

def get_args():
    parser = argparse.ArgumentParser(
        '''
        GraphQLer - a stateful fuzzing tool on GraphQL
        '''
    )

    parser.add_argument(
        '--mode','-mode',
        required=True,
        type=str,
        choices=["compile", "fuzz", "debug"],
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
        '--introspection-json', '-i',
        type=str
    )

    parser.add_argument(
        '--save', '-o',
        type=str
    )

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
                schema_builder = parse.SchemaBuilder(introspection_json=json.load(f))
        else:
            raise Exception("please add corrent introspection source to arguments by --url or --introspection-json")

        print(schema_builder.prepared_schema)

        if args.save:
            schema_builder.dump(path=args.save)
        else:
            schema_builder.dump()
        
        
    if args.mode == 'debug':
        url = args.url
        introspection_json_path = args.introspection_json
        if url:
            schema_builder = parse.SchemaBuilder(url=url)
        elif introspection_json_path:
            with open(introspection_json_path) as f:
                schema_builder = parse.SchemaBuilder(introspection_json=json.load(f))
        else:
            raise Exception("please add corrent introspection source to arguments by --url or --introspection-json")


        selected_query = schema_builder.prepared_schema["queries"]["messages"]
        selected_query.prepare_payload(schema_builder.schema["inputObjects"], schema_builder.schema["objects"])
        print(selected_query.stringify_payload(selected_query.prepared_payload))
        
        pprint(selected_query.prepared_payload)

        request = request.Request(url, request.Request.MODE_QUERY)
        request.add_payload(selected_query.stringify_payload(selected_query.prepared_payload))
        

        print(request.get_request_body())
        print(request.request())