import argparse
import time
from os import error
import introspection.parse as parse

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
        required=True,
        type=str
    )
    parser.add_argument(
        '--save', '-s',
        type=str
    )

    return parser


if __name__ == '__main__':
    args = get_args().parse_args()

    if args.compile:
        url = args.url
        
        schema_builder = parse.SchemaBuilder(url)
        
        if args.save:
            schema_builder.dump(path=args.save)
        
        