import gzip
import json
import os
import re
import statistics
from collections import namedtuple
from typing import IO, Dict, Generator, List

LogFile = namedtuple("LogFile", ["name", "date", "extention"])
ParserOutput = namedtuple("ParserOutput", ["entries", "total"])

config: Dict = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
}


def is_config_defined(argv: List[str]) -> bool:
    return "--config" in argv


def get_config_path(argv: List[str]) -> str:
    try:
        return argv[argv.index("--config") + 1]
    except IndexError:
        return ""


def read_config(config_path: str) -> str:
    if not config_path:
        return ""

    return open(config_path, encoding="utf-8").read()


def load_config(config_text: str) -> Dict:
    if not config_text:
        return {}

    return json.loads(config_text)


def apply_config(app_config: Dict, ext_config: Dict) -> Dict:
    if not app_config:
        return {}

    if not ext_config:
        return {}

    app_config.update(ext_config)
    return app_config


def is_log_dir_exists(dir_path: str) -> bool:
    if not dir_path:
        return False

    return os.path.exists(dir_path)


def get_log_files(dir_path: str) -> List[str]:
    return os.listdir(dir_path)


def search_latest(log_files: List[str]) -> LogFile:
    search_pattern = r"^nginx-access-ui\.log-(?P<date>\d{8})(?:\.gz)?$"

    latest_date = "00000000"
    latest_log = ""

    for log_name in log_files:
        name_match = re.search(search_pattern, log_name)
        if name_match:
            date = name_match.group("date")
            if date > latest_date:
                latest_date = date
                latest_log = log_name

    return LogFile(latest_log, latest_date, ".gz" if ".gz" in latest_log else ".log")


def get_log_path(log_name: str, log_dir: str) -> str:
    return f"{log_dir}/{log_name}"


def entries_parser(log_file: IO[str]) -> Generator[Dict, None, None]:
    parsing_pattern = r"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+(?P<url>[^\s]+).*?\s+(?P<request_time>\d+\.\d+)$"

    idx = 0
    for line in log_file:
        idx += 1
        line_match = re.search(parsing_pattern, line)

        if line_match is None:
            yield {
                "error": f"Failed parsing {log_file.name} line {idx} `{line}` does not contains format matches"
            }

            continue

        yield line_match.groupdict()


def parse_entries(parser: Generator[Dict, None, None]) -> ParserOutput:
    entries: Dict = {}
    total: Dict = {"entries": 0, "request_time": 0.0}

    for entry in parser:
        if "error" in entry:
            # TODO: Parsing Error
            continue

        url = entry["url"]
        request_time = float(entry["request_time"])

        if url not in entries:
            entries[url] = []

        entries[url].append(request_time)

        total["entries"] += 1
        total["request_time"] += request_time

    return ParserOutput(entries, total)


def calculate_report_metrics(etnries: Dict, total: Dict) -> List[Dict]:
    metrics: List[Dict] = []

    for url in etnries:
        entry_metrics: Dict = {
            "url": url,
            "count": len(etnries[url]),
            "count_perc": len(etnries[url]) / total["entries"] * 100,
            "time_sum": sum(etnries[url]),
            "time_perc": sum(etnries[url]) / total["request_time"] * 100,
            "time_avg": statistics.mean(etnries[url]),
            "time_max": max(etnries[url]),
            "time_med": statistics.median(etnries[url]),
        }

        metrics.append(entry_metrics)

    return metrics


def is_report_dir_exists(report_dir: str):
    if not report_dir:
        return False

    return os.path.exists(report_dir)


def sort_metrics(metrics: List[Dict]) -> List[Dict]:
    metrics.sort(reverse=True, key=lambda d: (d.get("time_sum", 0.0), 0))
    return metrics


def truncate_metrics(metrics: List[Dict], size: int) -> List[Dict]:
    metrics = metrics[0:size]
    return metrics


def get_json_metrics(metrics: List[Dict]) -> str:
    return json.dumps(metrics)


def get_report_template(template_path: str) -> str:
    return open(template_path, encoding="utf-8").read()


def get_report_content(template: str, json_metrics: str) -> str:
    return template.replace("$table_json", json_metrics)


def get_report_path(report_dir: str, report_date: str) -> str:
    return f"{report_dir}/report-{report_date}.html"


def save_report(report_path: str, report_content: str) -> int:
    return open(report_path, mode="w", encoding="utf-8").write(report_content)


def main(argv: List[str]) -> None:
    app_config = config.copy()

    if is_config_defined(argv):
        ext_config_path = get_config_path(argv)
        ext_config_text = read_config(ext_config_path)
        ext_config = load_config(ext_config_text)
        app_config = apply_config(app_config, ext_config)

    log_dir = app_config["LOG_DIR"]
    report_dir = app_config["REPORT_DIR"]

    if not is_log_dir_exists(log_dir):
        # TODO: Log error: dir not exists
        exit()

    log_files = get_log_files(log_dir)

    if not log_files:
        # TODO: Log error: dir empty
        exit()

    latest_log = search_latest(log_files)

    if not latest_log or not latest_log.name:
        # TODO: Log error : latest file not found
        exit()

    log_path = get_log_path(latest_log.name, log_dir)
    log_file: IO[str] = (
        gzip.open(log_path, mode="rt", encoding="utf-8")
        if latest_log.extention == ".gz"
        else open(log_path, encoding="utf-8")
    )

    parser = entries_parser(log_file)
    parser_output = parse_entries(parser)

    metrics = calculate_report_metrics(parser_output.entries, parser_output.total)
    metrics = sort_metrics(metrics)
    metrics = truncate_metrics(metrics, 2)
    metrics_json = get_json_metrics(metrics)

    if not is_report_dir_exists(report_dir):
        # TODO: Log error: dir not exists
        exit()

    report_template = get_report_template("report.html")
    report_content = get_report_content(report_template, metrics_json)
    report_path = get_report_path(report_dir, latest_log.date)
    save_report(report_path, report_content)
