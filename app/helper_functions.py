import yaml

def read_yaml(file_name) -> dict:
    with open(file_name, "r") as stream:
        yaml_dict = yaml.safe_load(stream)

    return yaml_dict

