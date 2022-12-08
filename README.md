
# GraphQLer 2022 

### Setup

Create the virtual environment

```shell
python3 -m venv .env
```

Activate the virtual environment

```shell
source .env/bin/activate
```

Install dependencies

```shell
pip3 install -r requirements.txt
```



--------

### Basic Usage

Help info

```shell
python3 main.py --help

usage: 
        GraphQLer - a stateful fuzzing tool on GraphQL
        
       [-h] --mode {compile,fuzzing,debug_fuzzing} [--test] [--url URL]
       [--wordlist WORDLIST] [--introspection-json INTROSPECTION_JSON] [--save SAVE]
       [--schema SCHEMA]

options:
  -h, --help            show this help message and exit
  --mode {compile,fuzzing,debug_fuzzing}, -mode {compile,fuzzing,debug_fuzzing}
  --test, -t
  --url URL, -u URL
  --wordlist WORDLIST, -w WORDLIST
  --introspection-json INTROSPECTION_JSON, -i INTROSPECTION_JSON
  --save SAVE, -o SAVE
  --schema SCHEMA
```



--------

### Building Test Schema

Build from Introspection JSON file

```shell
python3 main.py --mode compile --introspection-json <introspection-json-file-path> --save <dir-to-save-schemas>
```

or, Build from GraphQL server URL

```shell
python3 main.py --mode compile -u <GraphQL-server-url> --save <dir-to-save-schemas>
```



Test Schemas will be saved to folder `<dir-to-save-schemas>`, including:

```
<dir-to-save-schemas>
|____schema.json					// parsed GraphQL schema JSON
|____query_parameter_list.yml		// description of GraphQL Query parameters
|____mutation_parameter_list.yml	// description of GraphQL Mutation parameters
|____mutation_function_list.yml		// description of GraphQL Mutation function types ("Create" | "Update" | "Delete")
```



-------

### Fuzzing Testing

We could use `fuzzing` mode to do fuzzing tests after preparing the test schemas.

```shell
python3 main.py --mode fuzzing -u <GraphQL-server-url> --schema <dir-of-schemas>
```

The path `<dir-of-schemas>` is the previously created schema directory (generated from `compile` mode).

After testing, results will be saved in `<dir-of-schemas>/results.txt`.



