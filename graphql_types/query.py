from graphql_types import callable


class Query(callable.Callable):
    def __init__(self, name, schema_json=None, args_schema=None):
        super().__init__(
            name,
            schema_json=schema_json,
            args_schema=args_schema
        )
