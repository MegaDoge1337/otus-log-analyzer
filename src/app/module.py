import gzip
import json
import os
import re
import statistics
import sys
from datetime import datetime
from typing import IO, Dict, Optional, Tuple, Union

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

    name_pattern = r"nginx-access-ui\.log-(?P<date>\d{8})"

    latest_log = None
    latest_date = None

    logs_list = os.listdir(dir_path)

    for log in logs_list:
        name_match = re.search(name_pattern, log)

        if name_match is None:
            print(f"Skipped {log}...")
            continue

        date = name_match.group("date") if name_pattern else None

        # if date none ???

        log_date = datetime.strptime(str(date), "%Y%m%d")

        if latest_log is None and latest_date is None:
            latest_log = log
            latest_date = log_date

        if log_date > latest_date:
            latest_log = log
            latest_date = log_date

    if latest_log is None or latest_date is None:
        return None

    return f"{dir_path}/{latest_log}", latest_date


def open_log_file(log_path: str) -> IO[str]:
    if ".gz" in log_path:
        return gzip.open(log_path, mode="rt", encoding="utf-8")

    return open(log_path, encoding="utf-8")


def parse_log_entries(log_file: IO[str]):
    log_lines = log_file.readlines()

    line_pattern = r'"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+(?P<url>[^\s]+).*?"\s+(?P<request_time>\d+\.\d+)$'

    for idx, line in enumerate(log_lines):
        line_match = re.search(line_pattern, line)
        if line_match:
            yield line_match.groupdict()
        else:
            yield {
                "error": f"Failed parsing file {log_file.name}: line {idx + 1} does not contains format matches"
            }


def build_report(log_file: IO[str], entries_parser):
    entries_stats: Dict[str, list[float]] = {}
    total_stats = {"entries": 0, "request_time": 0.0}

    for entry in entries_parser(log_file):
        if "error" in entry:
            print(entry["error"])
            continue

        url = entry["url"]
        request_time = float(entry["request_time"])

        if url not in entries_stats:
            entries_stats[url] = []

        entries_stats[url].append(request_time)

        total_stats["entries"] += 1
        total_stats["request_time"] += request_time

    report_data = []

    for entry in entries_stats:
        entry_data = {
            "url": entry,
            "count": len(entries_stats[entry]),
            "count_perc": len(entries_stats[entry]) / total_stats["entries"] * 100,
            "time_sum": sum(entries_stats[entry]),
            "time_perc": sum(entries_stats[entry]) / total_stats["request_time"] * 100,
            "time_avg": statistics.mean(entries_stats[entry]),
            "time_max": max(entries_stats[entry]),
            "time_med": statistics.median(entries_stats[entry]),
        }

        report_data.append(entry_data)


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

    log_file = open_log_file(latest_log_path)
    build_report(log_file, parse_log_entries)
