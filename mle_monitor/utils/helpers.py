import yaml
import commentjson
from dotmap import DotMap
import re
import logging
from rich.logging import RichHandler


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


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def setup_logger(logging_level: int = logging.INFO):
    logging.basicConfig(
        level=logging_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    return logger
