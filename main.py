import argparse
import time
from os import error
import introspection.parse as parse
import json

def get_args():
    parser = argparse.ArgumentParser(
        '''
        a stateful fuzzing tool on GraphQL - GraphQLer
        '''
    )
    parser.add_argument(
        "compile",
        nargs="+"
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

    if args.compile:
        url = args.url
        introspection_json_path = args.introspection_json
        if url:
            schema_builder = parse.SchemaBuilder(url=url)
        elif introspection_json_path:
            with open(introspection_json_path) as f:
                schema_builder = parse.SchemaBuilder(introspection_json=json.load(f))

        if args.save:
            schema_builder.dump(path=args.save)
        
        