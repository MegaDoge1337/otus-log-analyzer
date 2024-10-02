import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseReportBuilder(ABC):
    @abstractmethod
    def sort_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        pass

    @abstractmethod
    def truncate_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        pass

    @abstractmethod
    def convert_metrics_to_json(self) -> str:
        pass

    @abstractmethod
    def build_report_path(self) -> str:
        pass

    @abstractmethod
    def insert_into_template(self, report_metrics_json: str) -> Union[str, None]:
        pass

    @abstractmethod
    def save_report(self, report_content: str, report_path: str) -> None:
        pass

    @abstractmethod
    def make_report(self):
        pass


class ReportBuilder(BaseReportBuilder):
    def __init__(
        self,
        report_metrics: List[Dict[str, Union[str, int, float]]],
        report_size: int,
        report_dir: str,
        report_date: str,
        report_template_path: str,
    ) -> None:
        self.__report_metrics = report_metrics
        self.__report_size = report_size
        self.__report_dir = report_dir
        self.__report_date = report_date
        self.__report_template_path = report_template_path

    def sort_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        self.__report_metrics.sort(
            reverse=True, key=lambda d: (d.get("time_sum", 0.0), 0)
        )
        return self.__report_metrics

    def truncate_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        self.__report_metrics = self.__report_metrics[0 : self.__report_size]
        return self.__report_metrics

    def convert_metrics_to_json(self) -> str:
        return json.dumps(self.__report_metrics)

    def build_report_path(self) -> str:
        return f"{self.__report_dir}/report-{self.__report_date}.html"

    def insert_into_template(self, report_metrics_json: str) -> Union[str, None]:
        if not os.path.exists(self.__report_template_path):
            return None

        report_content = open(self.__report_template_path, encoding="utf-8").read()
        return report_content.replace("$table_json", report_metrics_json)

    def save_report(self, report_content: str, report_path: str) -> None:
        if not os.path.exists(self.__report_template_path):
            return None

        open(report_path, mode="w", encoding="utf-8").write(report_content)

    def make_report(self) -> None:
        self.sort_report_metrics()
        self.truncate_report_metrics()

        report_metrics_json = self.convert_metrics_to_json()
        report_path = self.build_report_path()
        report_content = self.insert_into_template(report_metrics_json)

        if report_content is not None:
            self.save_report(str(report_content), report_path)
