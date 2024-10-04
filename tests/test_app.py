import json
import os
from typing import Optional

import pytest

import src.app.module as app

app._configure_logger(None)


@pytest.fixture
def sample_parser_output():
    entries = {"/index.html": [0.1, 0.2, 0.3], "/api/data": [0.4, 0.5], "/about": [0.6]}
    total = {"entries": 6, "request_time": 2.1}
    return entries, total


@pytest.fixture
def sample_metrics():
    return [
        {"url": "/page1", "time_sum": 10.5},
        {"url": "/page2", "time_sum": 5.2},
        {"url": "/page3", "time_sum": 15.7},
        {"url": "/page4", "time_sum": 8.3},
        {"url": "/page5"},
        {"url": "/page6", "time_sum": 15.7},
    ]


@pytest.mark.parametrize(
    "argv,expected",
    [
        (["--config", "config.json"], True),
        (["other", "--config", "path/to/config.json"], True),
        (["--config"], True),
        ([], False),
        (["other", "args"], False),
        (["--conf", "config.json"], False),
        (["--CONFIG"], False),
        (["--Config"], False),
        (["--config", "config1.json", "--config", "config2.json"], True),
        (["arg1", "--config", "arg2"], True),
        (["arg1", "arg2", "--config"], True),
        (["--conf"], False),
    ],
)
def test_is_config_defined(argv, expected):
    assert app.is_config_defined(argv) == expected


def test_read_config(tmp_path):
    assert app.read_config("") == ""

    temp_file = tmp_path / "test_config.txt"
    temp_file.write_text("test configuration content", encoding="utf-8")

    assert app.read_config(str(temp_file)) == "test configuration content"

    non_existent_file = tmp_path / "non_existent_file.txt"

    assert app.read_config(str(non_existent_file)) == ""


def test_load_config():
    assert app.load_config("") == {}

    valid_json = '{"key": "value", "number": 42, "list": [1, 2, 3]}'
    expected_result = {"key": "value", "number": 42, "list": [1, 2, 3]}
    assert app.load_config(valid_json) == expected_result

    invalid_json = '{"key": "value",}'
    assert app.load_config(invalid_json) == {}

    empty_json = "{}"
    assert app.load_config(empty_json) == {}

    json_array = "[1, 2, 3]"
    assert app.load_config(json_array) == [1, 2, 3]

    nested_json = '{"outer": {"inner": "value"}, "array": [{"key": "value"}]}'
    expected_nested = {"outer": {"inner": "value"}, "array": [{"key": "value"}]}
    assert app.load_config(nested_json) == expected_nested


def test_apply_config():
    assert app.apply_config({}, {}) == {}

    assert app.apply_config({}, {"key": "value"}) == {}

    assert app.apply_config({"key": "value"}, {}) == {}

    app_config = {"app_key": "app_value"}
    ext_config = {"ext_key": "ext_value"}
    expected = {"app_key": "app_value", "ext_key": "ext_value"}
    assert app.apply_config(app_config, ext_config) == expected

    app_config = {"key": "app_value", "app_key": "app_value"}
    ext_config = {"key": "ext_value", "ext_key": "ext_value"}
    expected = {"key": "ext_value", "app_key": "app_value", "ext_key": "ext_value"}
    assert app.apply_config(app_config, ext_config) == expected

    app_config = {"nested": {"inner": "app_value"}}
    ext_config = {"nested": {"inner": "ext_value", "new": "new_value"}}
    expected = {"nested": {"inner": "ext_value", "new": "new_value"}}
    assert app.apply_config(app_config, ext_config) == expected

    original_app_config = {"key": "app_value"}
    original_ext_config = {"key": "ext_value"}
    app_config_copy = original_app_config.copy()
    ext_config_copy = original_ext_config.copy()

    app.apply_config(app_config_copy, ext_config_copy)

    assert original_app_config == {"key": "app_value"}
    assert original_ext_config == {"key": "ext_value"}


def test_is_log_dir_exists(tmp_path):
    existing_dir = tmp_path / "existing_dir"
    existing_dir.mkdir()

    non_existing_dir = tmp_path / "non_existing_dir"

    file_path = tmp_path / "file.txt"
    file_path.touch()

    assert app.is_log_dir_exists(str(existing_dir))
    assert not app.is_log_dir_exists(str(non_existing_dir))
    assert not app.is_log_dir_exists(None)
    assert not app.is_log_dir_exists("")
    assert app.is_log_dir_exists(str(file_path))
    assert app.is_log_dir_exists("/")


def test_get_log_files(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    (log_dir / "log1.txt").touch()
    (log_dir / "log2.txt").touch()
    (log_dir / "not_a_log.txt").touch()

    (log_dir / "subdir").mkdir()

    result = app.get_log_files(str(log_dir))

    assert set(result) == {"log1.txt", "log2.txt", "not_a_log.txt", "subdir"}
    assert len(result) == 4

    assert app.get_log_files(str(tmp_path / "non_existent")) == []
    assert app.get_log_files(str(log_dir / "log1.txt")) == []
    assert app.get_log_files(None) == []
    assert app.get_log_files("") == []


def test_search_latest():
    log_files = [
        "nginx-access-ui.log-20230601.gz",
        "nginx-access-ui.log-20230602",
        "nginx-access-ui.log-20230603.gz",
        "nginx-access-ui.log-20230604",
        "nginx-access-ui.log-20230605.bz2",
        "nginx-access-ui.log-20230605.zip",
        "nginx-access-ui.log-20230605.gz",
        "nginx-access-ui.log-20230605",
    ]

    result = app.search_latest(log_files)

    assert result.date == "20230605"
    assert result.name == "nginx-access-ui.log-20230605.gz"
    assert result.extention == ".gz"

    log_files.append("nginx-access-ui.log-20230606")

    result_with_newer = app.search_latest(log_files)

    assert result_with_newer.date == "20230606"
    assert result_with_newer.name == "nginx-access-ui.log-20230606"
    assert result_with_newer.extention == ".log"

    log_files_same_date = [
        "nginx-access-ui.log-20230605",
        "nginx-access-ui.log-20230605.gz",
    ]

    result_with_same_date = app.search_latest(log_files_same_date)

    assert result_with_same_date.date == "20230605"
    assert result_with_same_date.name == "nginx-access-ui.log-20230605"
    assert result_with_same_date.extention == ".log"

    # Проверяем случай с пустым списком
    empty_result = app.search_latest([])
    assert empty_result == app.LogFile("", "00000000", ".log")

    no_match_result = app.search_latest(["some-other-file.log", "not-matching-file.gz"])
    assert no_match_result == app.LogFile("", "00000000", ".log")


@pytest.mark.parametrize(
    "log_name, log_dir, expected",
    [
        ("access.log", "/var/log", "/var/log/access.log"),
        ("error.log", "/tmp", "/tmp/error.log"),
        ("app.log", None, ""),
        ("", "/var/log", ""),
        ("system.log", "", ""),
    ],
)
def test_get_log_path(log_name: str, log_dir: Optional[str], expected: str):
    result = app.get_log_path(log_name, log_dir)
    assert result == expected


def test_entries_parser(tmp_path):
    log_content = [
        '192.168.1.1 - - [01/Jan/2023:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0" 0.123\n',
        '192.168.1.2 - - [01/Jan/2023:00:00:02 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "PostmanRuntime/7.28.4" 0.456\n',
        '192.168.1.3 - - [01/Jan/2023:00:00:03 +0000] "Invalid log entry" 400 100 "-" "-" 0.789\n',
        '192.168.1.4 - - [01/Jan/2023:00:00:04 +0000] "PUT /update HTTP/1.1" 204 0 "-" "curl/7.68.0" 0.234\n',
    ]

    log_file = tmp_path / "test_log.txt"

    with open(log_file, mode="w", encoding="utf-8") as file:
        file.writelines(log_content)

    with open(log_file, encoding="utf-8") as file:
        parser = app.entries_parser(file)
        assert next(parser, None) == {"url": "/index.html", "request_time": "0.123"}
        assert next(parser, None) == {"url": "/api/data", "request_time": "0.456"}
        assert next(parser, None) == {}
        assert next(parser, None) == {"url": "/update", "request_time": "0.234"}
        assert next(parser, None) is None


def test_parse_entries(tmp_path):
    log_content = [
        '192.168.1.1 - - [01/Jan/2023:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0" 0.123\n',
        '192.168.1.2 - - [01/Jan/2023:00:00:02 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "PostmanRuntime/7.28.4" 0.456\n',
        '192.168.1.3 - - [01/Jan/2023:00:00:03 +0000] "Invalid log entry" 400 100 "-" "-" 0.789\n',
        '192.168.1.4 - - [01/Jan/2023:00:00:04 +0000] "PUT /update HTTP/1.1" 204 0 "-" "curl/7.68.0" 0.234\n',
    ]

    log_file = tmp_path / "test_log.txt"

    with open(log_file, mode="w", encoding="utf-8") as file:
        file.writelines(log_content)

    with open(log_file, encoding="utf-8") as file:
        parser = app.entries_parser(file)
        result = app.parse_entries(parser)

    assert len(result.entries) == 3

    assert result.entries["/index.html"] == [0.123]
    assert result.entries["/api/data"] == [0.456]
    assert result.entries["/update"] == [0.234]

    assert result.total["entries"] == 3
    assert result.total["request_time"] == 0.813


def test_calculate_metrics(sample_parser_output):
    entries, total = sample_parser_output

    result = app.calculate_metrics(entries, total)

    assert len(result) == 3

    for entry in result:
        if entry["url"] == "/index.html":
            assert entry["count"] == 3
            assert entry["count_perc"] == pytest.approx(50.0)
            assert entry["time_sum"] == 0.6
            assert entry["time_perc"] == pytest.approx(28.57, rel=1e-2)
            assert entry["time_avg"] == 0.2
            assert entry["time_max"] == 0.3
            assert entry["time_med"] == 0.2
        elif entry["url"] == "/api/data":
            assert entry["count"] == 2
            assert entry["count_perc"] == pytest.approx(33.33, rel=1e-2)
            assert entry["time_sum"] == 0.9
            assert entry["time_perc"] == pytest.approx(42.86, rel=1e-2)
            assert entry["time_avg"] == 0.45
            assert entry["time_max"] == 0.5
            assert entry["time_med"] == 0.45
        elif entry["url"] == "/about":
            assert entry["count"] == 1
            assert entry["count_perc"] == pytest.approx(16.67, rel=1e-2)
            assert entry["time_sum"] == 0.6
            assert entry["time_perc"] == pytest.approx(28.57, rel=1e-2)
            assert entry["time_avg"] == 0.6
            assert entry["time_max"] == 0.6
            assert entry["time_med"] == 0.6
        else:
            pytest.fail(f"Unexpected URL: {entry['url']}")

    total_count_perc = sum(entry["count_perc"] for entry in result)
    total_time_perc = sum(entry["time_perc"] for entry in result)
    assert total_count_perc == pytest.approx(100.0)
    assert total_time_perc == pytest.approx(100.0)


@pytest.mark.parametrize(
    "report_dir, expected_result",
    [
        (None, False),
        ("", False),
        ("/non/existent/directory", False),
        (os.path.dirname(__file__), True),
    ],
)
def test_is_report_dir_exists(
    report_dir: Optional[str], expected_result: bool, tmp_path
):
    if report_dir == "/non/existent/directory":
        report_dir = str(tmp_path / "non_existent")
    elif report_dir == os.path.dirname(__file__):
        report_dir = str(tmp_path)
        os.makedirs(report_dir, exist_ok=True)

    result = app.is_report_dir_exists(report_dir)
    assert result == expected_result


def test_sort_metrics(sample_metrics):
    sorted_metrics = app.sort_metrics(sample_metrics)
    expected_order = ["/page3", "/page6", "/page1", "/page4", "/page2", "/page5"]
    assert [m["url"] for m in sorted_metrics] == expected_order

    time_sums = [m.get("time_sum", 0.0) for m in sorted_metrics]
    assert time_sums == sorted(time_sums, reverse=True)

    assert sorted_metrics[-1]["url"] == "/page5"
    assert "time_sum" not in sorted_metrics[-1]

    assert sorted_metrics[0]["url"] == "/page3"
    assert sorted_metrics[1]["url"] == "/page6"

    for original, sorted_item in zip(sample_metrics, sorted_metrics):
        assert original is sorted_item

    assert app.sort_metrics([]) == []


def test_truncate_metrics(sample_metrics):
    result = app.truncate_metrics(sample_metrics, 3)
    assert len(result) == 3
    assert result == sample_metrics[:3]

    result = app.truncate_metrics(sample_metrics, 10)
    assert len(result) == 6
    assert result == sample_metrics

    result = app.truncate_metrics(sample_metrics, 0)
    assert len(result) == 0
    assert result == []

    result = app.truncate_metrics([], 5)
    assert len(result) == 0
    assert result == []

    result = app.truncate_metrics(sample_metrics, -1)
    assert len(result) == 5
    assert result == sample_metrics[0:5]

    original_input = sample_metrics.copy()
    app.truncate_metrics(sample_metrics, 2)
    assert sample_metrics == original_input

    result = app.truncate_metrics(sample_metrics, 2)
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


def test_get_json_metrics(sample_metrics):
    result = app.get_json_metrics(sample_metrics)

    assert isinstance(result, str)

    parsed_result = json.loads(result)
    assert isinstance(parsed_result, list)
    assert all(isinstance(item, dict) for item in parsed_result)

    assert parsed_result == sample_metrics

    empty_result = app.get_json_metrics([])
    assert empty_result == "[]"

    special_metrics = [{"url": "/page with spaces", "description": 'Test "quotes"'}]
    special_result = app.get_json_metrics(special_metrics)
    assert json.loads(special_result) == special_metrics

    nested_metrics = [{"url": "/page1", "nested": {"key": "value"}}]
    nested_result = app.get_json_metrics(nested_metrics)
    assert json.loads(nested_result) == nested_metrics


def test_get_report_template(tmp_path):
    template_content = """
  <html>
  <head><title>{{ title }}</title></head>
  <body>
  <h1>{{ header }}</h1>
  <p>{{ content }}</p>
  </body>
  </html>
  """
    template_file = tmp_path / "test_template.html"
    template_file.write_text(template_content, encoding="utf-8")

    result = app.get_report_template(str(template_file))

    assert result == template_content

    assert app.get_report_template(str(tmp_path / "non_existent_file.html")) == ""

    non_utf8_file = tmp_path / "non_utf8.html"
    non_utf8_file.write_bytes(b"\xFF\xFE" + "Non-UTF8 content".encode("utf-16-le"))

    assert app.get_report_template(str(non_utf8_file)) == ""


def test_insert_report_content():
    template = "This is a template with $table_json placeholder."
    json_metrics = '{"metric1": 10, "metric2": 20}'
    expected_output = (
        'This is a template with {"metric1": 10, "metric2": 20} placeholder.'
    )

    result = app.insert_report_content(template, json_metrics)

    assert result == expected_output

    assert app.insert_report_content("", "") == ""
    assert app.insert_report_content("No placeholder", "{}") == "No placeholder"
    assert app.insert_report_content("$table_json$table_json", "{}") == "{}{}"


def test_get_report_path():
    report_dir = "reports"
    report_date = "20230425"
    expected_path = "reports/report-20230425.html"

    result = app.get_report_path(report_dir, report_date)

    assert result == expected_path

    assert app.get_report_path(None, report_date) == ""
    assert app.get_report_path("", report_date) == ""
    assert (
        app.get_report_path("/path/to/reports", "20221231")
        == "/path/to/reports/report-20221231.html"
    )


def test_save_report(tmp_path):
    report_content = "This is a test report."
    report_path = tmp_path / "report.html"

    result = app.save_report(str(report_path), report_content)

    assert result == len(report_content)
    with open(report_path, encoding="utf-8") as file:
        saved_content = file.read()
    assert saved_content == report_content


def test_main(tmp_path):
    log_dir = tmp_path / "log"
    log_dir.mkdir()

    log_file = log_dir / "nginx-access-ui.log-20230605"
    log_file.write_text(
        '192.168.1.1 - - [01/Jan/2023:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0" 0.123\n'
        '192.168.1.2 - - [01/Jan/2023:00:00:02 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "PostmanRuntime/7.28.4" 0.456\n'
        '192.168.1.3 - - [01/Jan/2023:00:00:03 +0000] "Invalid log entry" 400 100 "-" "-" 0.789\n'
        '192.168.1.4 - - [01/Jan/2023:00:00:04 +0000] "PUT /update HTTP/1.1" 204 0 "-" "curl/7.68.0" 0.234\n'
    )

    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    config_text = json.dumps({"REPORT_DIR": str(report_dir), "LOG_DIR": str(log_dir)})
    config_file = tmp_path / "config.json"
    config_file.write_text(config_text)

    expected_report_path = report_dir / "report-20230605.html"

    app.main(["--config", str(config_file)])

    assert expected_report_path.exists()
    with open(expected_report_path, encoding="utf-8") as report_file:
        report_content = report_file.read()
    assert "$table_json" not in report_content
