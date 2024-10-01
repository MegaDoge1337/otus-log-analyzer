import time
import json
import sys

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


def is_external_config_defined() -> bool:
    return "--config" in sys.argv


def get_external_config_path():
    arg_key_index = sys.argv.index("--config")
    try:
        return sys.argv[arg_key_index + 1]
    except IndexError:
        print(
            "usage python main.py --config [config_path]\noptions:\n--config  Defined path to external configuration file"
        )
        return None


def read_external_config() -> dict:
    path = get_external_config_path()
    file_content = open(path).read()
    return json.loads(file_content)


def merge_configs(default_config: dict, external_config: dict):
    internal_config_keys = default_config.keys()
    for key in internal_config_keys:
        if key in external_config:
            default_config[key] = external_config[key]
    return default_config


def main():
    app_config = config

    if is_external_config_defined():
        external_config = read_external_config()
        app_config = merge_configs(app_config, external_config)

    print(app_config)
