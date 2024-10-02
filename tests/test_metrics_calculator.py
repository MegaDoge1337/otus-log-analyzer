import statistics
from typing import Dict, Union

import pytest

from src.app.metrics_calculator import MetricsCalculator


@pytest.fixture
def entries_info() -> Dict[str, list[float]]:
    return {"/api/v2/banner/25019354": [0.39, 0.2]}


@pytest.fixture
def total_info() -> Dict[str, Union[int, float]]:
    return {"entries": 2, "request_time": (0.39 + 0.2)}


def test_calculate_report_metrics(
    entries_info: Dict[str, list[float]], total_info: Dict[str, Union[int, float]]
) -> None:
    metrics_calculator = MetricsCalculator(entries_info, total_info)
    metrics = metrics_calculator.calculate_report_metrics()
    print(metrics)

    assert len(metrics) == 1

    assert "url" in metrics[0]
    assert "count" in metrics[0]
    assert "count_perc" in metrics[0]
    assert "time_sum" in metrics[0]
    assert "time_perc" in metrics[0]
    assert "time_avg" in metrics[0]
    assert "time_max" in metrics[0]
    assert "time_med" in metrics[0]

    assert metrics[0]["url"] == "/api/v2/banner/25019354"
    assert metrics[0]["count"] == len(entries_info["/api/v2/banner/25019354"])
    assert (
        metrics[0]["count_perc"]
        == len(entries_info["/api/v2/banner/25019354"]) / total_info["entries"] * 100
    )
    assert metrics[0]["time_sum"] == sum(entries_info["/api/v2/banner/25019354"])
    assert (
        metrics[0]["time_perc"]
        == sum(entries_info["/api/v2/banner/25019354"])
        / total_info["request_time"]
        * 100
    )
    assert metrics[0]["time_avg"] == statistics.mean(
        entries_info["/api/v2/banner/25019354"]
    )
    assert metrics[0]["time_max"] == max(entries_info["/api/v2/banner/25019354"])
    assert metrics[0]["time_med"] == statistics.median(
        entries_info["/api/v2/banner/25019354"]
    )
