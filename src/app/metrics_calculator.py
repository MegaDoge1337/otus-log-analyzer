import statistics
from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseMetricsCalculator(ABC):
    @abstractmethod
    def calculate_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        pass


class MetricsCalculator(BaseMetricsCalculator):
    def __init__(
        self,
        entries_info: Dict[str, list[float]],
        total_info: Dict[str, Union[int, float]],
    ) -> None:
        self.__entries_info = entries_info
        self.__total_info = total_info

    def calculate_report_metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        metrics: List[Dict[str, Union[str, int, float]]] = []

        for url in self.__entries_info:
            entry_metrics: Dict[str, Union[str, int, float]] = {
                "url": url,
                "count": len(self.__entries_info[url]),
                "count_perc": len(self.__entries_info[url])
                / self.__total_info["entries"]
                * 100,
                "time_sum": sum(self.__entries_info[url]),
                "time_perc": sum(self.__entries_info[url])
                / self.__total_info["request_time"]
                * 100,
                "time_avg": statistics.mean(self.__entries_info[url]),
                "time_max": max(self.__entries_info[url]),
                "time_med": statistics.median(self.__entries_info[url]),
            }

            metrics.append(entry_metrics)

        return metrics
