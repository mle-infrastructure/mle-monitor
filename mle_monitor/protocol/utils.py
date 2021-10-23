import yaml
import commentjson
from dotmap import DotMap


def load_yaml_config(config_fname: str, return_dotmap: bool = False):
    """Load in YAML config file."""
    with open(config_fname) as file:
        yaml_config = yaml.load(file, Loader=yaml.FullLoader)
    if not return_dotmap:
        return yaml_config
    else:
        return DotMap(yaml_config)


def load_json_config(config_fname: str, return_dotmap: bool = False):
    """Load in JSON config file."""
    json_config = commentjson.loads(open(config_fname, "r").read())
    if not return_dotmap:
        return json_config
    else:
        return DotMap(json_config)
