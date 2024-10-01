import gzip
import json
import os
import re
import sys
from datetime import datetime
from typing import Callable, Dict, Optional, Tuple, Union

config: Dict[str, Union[str, int]] = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
}


def is_external_config_defined() -> bool:
    return "--config" in sys.argv


def get_external_config_path() -> str:
    arg_key_index = sys.argv.index("--config")
    return sys.argv[arg_key_index + 1]


def read_external_config() -> Dict[str, Union[str, int]]:
    path = get_external_config_path()
    file_content = open(path).read()
    return json.loads(file_content)


def merge_configs(
    default_config: Dict[str, Union[str, int]],
    external_config: Dict[str, Union[str, int]],
) -> Dict[str, Union[str, int]]:
    internal_config_keys = default_config.keys()
    for key in internal_config_keys:
        if key in external_config:
            default_config[key] = external_config[key]
    return default_config


def get_latest_log_path_with_date(
    dir_path: str,
) -> Optional[Tuple[str, datetime]]:
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exists")
        return None

    date_pattern = r"\d{8}"

    latest_log = None
    latest_date = None

    logs_list = os.listdir(dir_path)

    for log in logs_list:
        date_match = re.search(date_pattern, log)
        date = date_match.group() if date_match else None

        if date is None:
            print(f"Date in log name {log} is not defined, skipped...")
            continue

        log_date = datetime.strptime(date, "%Y%m%d")

        latest_log = log if latest_log is None else latest_log
        latest_date = log_date if latest_date is None else latest_date

        if log_date > latest_date:
            latest_log = log
            latest_date = log_date

    if latest_log is None or latest_date is None:
        return None

    return f"{dir_path}/{latest_log}", latest_date


def get_log_reader(log_path: str) -> Callable:
    if ".gz" in log_path:
        return gzip.open

    return open


def main() -> None:
    app_config: Dict[str, Union[str, int]] = config

    if is_external_config_defined():
        external_config = read_external_config()
        app_config = merge_configs(app_config, external_config)

    print(app_config)

    log_dir = str(app_config["LOG_DIR"])
    latest_log_data = get_latest_log_path_with_date(log_dir)

    if latest_log_data is None:
        return None

    latest_log_path, _ = latest_log_data

    _ = get_log_reader(latest_log_path)
