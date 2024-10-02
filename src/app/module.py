from typing import Dict, List, Union

from src.app.config_manager import ConfigManager
from src.app.log_file_manager import LogFileManager
from src.app.metrics_calculator import MetricsCalculator
from src.app.parser import Parser
from src.app.report_builder import ReportBuilder

config: Dict[str, Union[str, int]] = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
}


class HomeworkAnalyzer:
    def analyze_and_save_report(self, argv: List[str]) -> None:

        app_config = ConfigManager(config).apply_external_config(argv)

        name_regex_pattern = r"^nginx-access-ui\.log-(?P<date>\d{8})(?:\.gz)?$"
        line_regex_pattern = r"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+(?P<url>[^\s]+).*?\s+(?P<request_time>\d+\.\d+)$"

        log_dir = str(app_config["LOG_DIR"])
        report_size = int(app_config["REPORT_SIZE"])
        report_dir = str(app_config["REPORT_DIR"])

        log_file_manager = LogFileManager(name_regex_pattern, log_dir)
        latest_log_data = log_file_manager.search_latest_log_file()

        if latest_log_data is None:
            return None

        latest_log, latest_date = latest_log_data

        latest_log_path = f"{log_dir}/{latest_log}"

        log_file, _ = log_file_manager.open_log_file(latest_log_path)

        parser = Parser(line_regex_pattern, log_file)

        entries_info, total_info = parser.get_entries_info()

        metrics_calculator = MetricsCalculator(entries_info, total_info)

        metrics = metrics_calculator.calculate_report_metrics()

        report_builder = ReportBuilder(
            metrics, report_size, report_dir, latest_date, "report.html"
        )

        report_builder.make_report()
