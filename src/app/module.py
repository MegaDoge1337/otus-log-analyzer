import gzip
import json
import os
import re
import statistics
import sys
from typing import IO, Dict, Generator, List, Optional, Tuple, Union

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


def read_external_config(config_path: str) -> Dict[str, Union[str, int]]:
    path = config_path
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


def search_latest_log(
    dir_path: str,
) -> Optional[Tuple[str, str]]:
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exists")
        return None

    name_pattern = r"^nginx-access-ui\.log-(?P<date>\d{8})(?:\.gz)?$"

    logs_list = os.listdir(dir_path)
    latest_date = "00000000"
    latest_log = ""

    for log_name in logs_list:
        name_match = re.search(name_pattern, log_name)
        if name_match:
            date = name_match.group("date")
            if date > latest_date:
                latest_date = date
                latest_log = log_name

    return latest_log, latest_date


def open_log_file(log_path: str) -> IO[str]:
    if ".gz" in log_path:
        return gzip.open(log_path, mode="rt", encoding="utf-8")

    return open(log_path, encoding="utf-8")


def parse_log_entries(log_file: IO[str]) -> Generator[Dict[str, str], None, None]:
    line_pattern = r"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+(?P<url>[^\s]+).*?\s+(?P<request_time>\d+\.\d+)$"
    idx = 0

    for line in log_file:
        idx += 1
        line_match = re.search(line_pattern, line)

        if line_match is None:
            yield {
                "error": f"Failed parsing {log_file.name} line {idx} `{line}` does not contains format matches"
            }

            continue

        yield line_match.groupdict()


def aggregate_entries_info(entries_parser: Generator[Dict[str, str], None, None]):
    entries_info: Dict[str, list[float]] = {}
    total_info = {"entries": 0, "request_time": 0.0}

    for entry in entries_parser:
        if "error" in entry:
            print(entry)
            continue

        url = entry["url"]
        request_time = float(entry["request_time"])

        if url not in entries_info:
            entries_info[url] = []

        entries_info[url].append(request_time)

        total_info["entries"] += 1
        total_info["request_time"] += request_time

    return entries_info, total_info


def calculate_report_metrics(
    entries_info: Dict[str, list[float]], total_info: Dict[str, Union[int, float]]
) -> List[Dict[str, Union[str, int, float]]]:
    report_metrics: List[Dict[str, Union[str, int, float]]] = []

    for url in entries_info:
        entry_metrics: Dict[str, Union[str, int, float]] = {
            "url": url,
            "count": len(entries_info[url]),
            "count_perc": len(entries_info[url]) / total_info["entries"] * 100,
            "time_sum": sum(entries_info[url]),
            "time_perc": sum(entries_info[url]) / total_info["request_time"] * 100,
            "time_avg": statistics.mean(entries_info[url]),
            "time_max": max(entries_info[url]),
            "time_med": statistics.median(entries_info[url]),
        }

        report_metrics.append(entry_metrics)

    return report_metrics


def filter_report_metrics(
    report_metrics: List[Dict[str, Union[str, int, float]]], report_size: int
) -> List[Dict[str, Union[str, int, float]]]:
    report_metrics.sort(reverse=True, key=lambda d: (d.get("time_sum", 0.0), 0))
    return report_metrics[0:report_size]


def generate_report(
    report_metrics_json: str, report_date: str, report_dir: str
) -> None:
    template_name = "report.html"

    if not os.path.exists(template_name):
        return None

    report_content = open(template_name, encoding="utf-8").read()
    report_content = report_content.replace("$table_json", report_metrics_json)

    report_path = f"{report_dir}/report-{report_date}.html"
    open(report_path, mode="w", encoding="utf-8").write(report_content)


def analyze() -> None:
    app_config: Dict[str, Union[str, int]] = config

    if is_external_config_defined():
        external_config_path = get_external_config_path()
        external_config = read_external_config(external_config_path)
        app_config = merge_configs(app_config, external_config)

    log_dir = str(app_config["LOG_DIR"])
    report_size = int(app_config["REPORT_SIZE"])
    report_dir = str(app_config["REPORT_DIR"])

    latest_log_data = search_latest_log(log_dir)

    if latest_log_data is None:
        return None

    latest_log, latest_date = latest_log_data

    latest_log_path = f"{log_dir}/{latest_log}"

    log_file = open_log_file(latest_log_path)

    entries_parser = parse_log_entries(log_file)

    entries_info, total_info = aggregate_entries_info(entries_parser)

    report_metrics = calculate_report_metrics(entries_info, total_info)

    filtered_report_metrics = filter_report_metrics(report_metrics, report_size)

    report_metrics_json = json.dumps(filtered_report_metrics)

    generate_report(report_metrics_json, latest_date, report_dir)
