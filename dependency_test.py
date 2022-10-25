import yaml

file = open("type.yml", "r")
data_type = yaml.safe_load(file)

print(data_type)

# TODO: 1. REWRITE OUTPUT FORMAT. 