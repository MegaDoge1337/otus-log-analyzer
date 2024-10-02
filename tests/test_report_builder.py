import json
import os
from pathlib import Path
from typing import Dict, List, Union

import pytest

from src.app.report_builder import ReportBuilder


@pytest.fixture
def report_size() -> int:
    return 1


@pytest.fixture
def report_dir_with_temlate(tmp_path) -> Path:

    template = tmp_path / "template.html"
    template.write_text("$table_json")

    return tmp_path


@pytest.fixture
def report_dir() -> str:
    return "./report"


@pytest.fixture
def report_date() -> str:
    return "20241002"


@pytest.fixture
def metrics() -> List[Dict[str, Union[str, int, float]]]:
    return [
        {
            "url": "/api/v2/banner/25019354",
            "count": 2,
            "count_perc": 100.0,
            "time_sum": 0.59,
            "time_perc": 100.0,
            "time_avg": 0.295,
            "time_max": 0.39,
            "time_med": 0.295,
        },
        {
            "url": "/api/v2/something/222222",
            "count": 2,
            "count_perc": 100.0,
            "time_sum": 25.67,
            "time_perc": 100.0,
            "time_avg": 0.295,
            "time_max": 0.39,
            "time_med": 0.295,
        },
    ]


def test_sort_report_metrics(
    report_size: int,
    report_dir_with_temlate: Path,
    report_date: str,
    metrics: List[Dict[str, Union[str, int, float]]],
) -> None:
    report_dir = str(report_dir_with_temlate)
    template = str(report_dir_with_temlate / "template.html")

    report_builder = ReportBuilder(
        metrics, report_size, report_dir, report_date, template
    )
    sorted_metrics = report_builder.sort_report_metrics()

    assert sorted_metrics[0]["url"] == "/api/v2/something/222222"
    assert sorted_metrics[1]["url"] == "/api/v2/banner/25019354"


def test_truncate_report_metrics(
    report_size: int,
    report_dir_with_temlate: Path,
    report_date: str,
    metrics: List[Dict[str, Union[str, int, float]]],
) -> None:
    report_dir = str(report_dir_with_temlate)
    template = str(report_dir_with_temlate / "template.html")

    report_builder = ReportBuilder(
        metrics, report_size, report_dir, report_date, template
    )
    truncated_metrics = report_builder.truncate_report_metrics()

    assert len(truncated_metrics) == 1


def test_convert_metrics_to_json(
    report_size: int,
    report_dir_with_temlate: Path,
    report_date: str,
    metrics: List[Dict[str, Union[str, int, float]]],
) -> None:
    report_dir = str(report_dir_with_temlate)
    template = str(report_dir_with_temlate / "template.html")

    report_builder = ReportBuilder(
        metrics, report_size, report_dir, report_date, template
    )
    metrics_json = report_builder.convert_metrics_to_json()

    assert json.loads(metrics_json)[0]["url"] == "/api/v2/banner/25019354"


def test_build_report_path(
    report_size: int,
    report_dir: str,
    report_date: str,
    metrics: List[Dict[str, Union[str, int, float]]],
) -> None:
    report_builder = ReportBuilder(
        metrics, report_size, report_dir, report_date, "no-template"
    )
    report_path = report_builder.build_report_path()

    assert report_path == "./report/report-20241002.html"


def test_make_report(
    report_size: int,
    report_dir_with_temlate: str,
    report_date: str,
    metrics: List[Dict[str, Union[str, int, float]]],
) -> None:
    report_dir = str(report_dir_with_temlate)
    template = f"{report_dir}/template.html"

    report_builder = ReportBuilder(
        metrics, report_size, report_dir, report_date, template
    )
    report_builder.make_report()

    assert os.path.exists(f"{report_dir}/report-20241002.html")
    assert (
        "$table_json"
        not in open(f"{report_dir}/report-20241002.html", encoding="utf-8").read()
    )
