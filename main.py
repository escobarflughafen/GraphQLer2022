import argparse
import os
import introspection.parse as parse
import json
from request import request
from pprint import pprint
from fuzzing.requestor import Requestor
from fuzzing.cache import Cache
from fuzzing.fuzzer.constant import ConstantFuzzer
from fuzzing.fuzzer.randomizer import RandomFuzzer
from fuzzing.fuzzer.wordlist import WordlistFuzzer
from graphql_types.process_functions import FunctionBuilder
from introspection.sequence import SequenceBuilder
from introspection.object_dependency import ObjectSequenceBuilder
from utils.logger import Logger


def get_args():
    parser = argparse.ArgumentParser(
        '''
        GraphQLer - a stateful fuzzing tool on GraphQL
        '''
    )

    parser.add_argument(
        '--mode', '-m',
        required=True,
        type=str,
        choices=["compile", "fuzzing"],
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

    parser.add_argument(
        '--fuzzer',
        type=str
    )

    parser.add_argument(
        '--no-name-mapping',
        action='store_true'
    )

    return parser


if __name__ == '__main__':
    args = get_args().parse_args()
    test = args.test
    schema_file_name = 'schema.json'
    function_list_file_name = 'mutation_function_list.yml'
    query_parameter_file_name = 'query_parameter_list.yml'
    mutation_parameter_file_name = 'mutation_parameter_list.yml'

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

        if args.save:
            if not os.path.isdir(args.save):
                os.mkdir(args.save)

            schema_builder.dump(path=os.path.join(args.save, schema_file_name))
        else:
            raise Exception("Need to specify a path to save schema files.")

        function_builder = FunctionBuilder(
            os.path.join(args.save, schema_file_name),
            no_scalar_datatype_mapping=args.no_name_mapping
        )
        function_builder.generate_grammar_file(args.save)

    elif args.mode == 'fuzzing':

        url = args.url
        parsed_schema_path = args.schema
        if not os.path.isdir(parsed_schema_path):
            raise Exception("FUZZING: Directory doesn't exist")

        with open(os.path.join(parsed_schema_path, schema_file_name)) as f:
            schema = json.load(f)

        function_builder = FunctionBuilder(
            os.path.join(parsed_schema_path, schema_file_name),
            function_list_file_path=os.path.join(
                parsed_schema_path, function_list_file_name),
            query_parameter_file_path=os.path.join(
                parsed_schema_path, query_parameter_file_name),
            mutation_parameter_file_path=os.path.join(
                parsed_schema_path, mutation_parameter_file_name),

        )

        obj_seq_builder = ObjectSequenceBuilder(
            os.path.join(parsed_schema_path, schema_file_name))
        sequence_builder = SequenceBuilder(

            obj_seq_builder.build_sequence()[0],
            function_builder
        )

        req_seq = sequence_builder.build_request_sequence()

        cache = Cache(schema)
        logger = Logger(parsed_schema_path)
        if args.fuzzer == 'constant':
            fuzzer = ConstantFuzzer(schema, cache)
        elif args.fuzzer == 'random':
            fuzzer = RandomFuzzer(schema, cache)
        elif args.fuzzer == 'wordlist':
            fuzzer = WordlistFuzzer(
                schema, cache, open(args.wordlist).readlines())
        else:
            fuzzer = RandomFuzzer(schema, cache)

        requestor = Requestor(req_seq,
                              cache,
                              fuzzer,
                              url,
                              schema,
                              function_builder,
                              logger
                              )

        requestor.execute(schema)
        logger.log()
        json.dump(requestor.errors, open(os.path.join(
            parsed_schema_path, 'errors.json'), 'w'))
