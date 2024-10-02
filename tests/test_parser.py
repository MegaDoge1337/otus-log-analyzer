from pathlib import Path

import pytest

from src.app.parser import Parser


@pytest.fixture
def default_line_regex_pattern() -> str:
    return r"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+(?P<url>[^\s]+).*?\s+(?P<request_time>\d+\.\d+)$"


@pytest.fixture
def temp_log_file(tmp_path) -> Path:
    log_file = tmp_path / "nginx-access-ui.log-20170630"

    log_file.write_text(
        "GET /api/v2/banner/25019354 0.390\n"
        "POST /api/v2/banner/25019354 0.200\n"
        "GET /api/v2/banner/25019354 +0.120\n"
        "GET /api/v2/banner/25019354 -0.050\n"
        "GET /api/v2/banner/25019354 123456\n"
        "GET /api/v2/banner/25019354 qwerty\n"
        "GET /api/v2/banner/25019354\n"
        "Sample text\n"
    )

    return log_file


def test_parse_log_entries(
    default_line_regex_pattern: str, temp_log_file: Path
) -> None:
    parser = Parser(default_line_regex_pattern, open(temp_log_file, encoding="utf-8"))

    # GET /api/v2/banner/25019354 0.390\n
    log_entry = next(parser.parse_log_entries())

    assert "url" in log_entry
    assert "request_time" in log_entry
    assert log_entry["url"] == "/api/v2/banner/25019354"
    assert log_entry["request_time"] == "0.390"

    # POST /api/v2/banner/25019354 0.200\n
    log_entry = next(parser.parse_log_entries())

    assert "url" in log_entry
    assert "request_time" in log_entry
    assert log_entry["url"] == "/api/v2/banner/25019354"
    assert log_entry["request_time"] == "0.200"

    # GET /api/v2/banner/25019354 +0.120\n
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry

    # GET /api/v2/banner/25019354 -0.050\n
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry

    # GET /api/v2/banner/25019354 123456\n
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry

    # GET /api/v2/banner/25019354 qwerty\n
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry

    # GET /api/v2/banner/25019354\n
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry

    # Sample text
    log_entry = next(parser.parse_log_entries())

    assert "url" not in log_entry
    assert "request_time" not in log_entry
    assert "error" in log_entry


def test_get_entries_info(default_line_regex_pattern: str, temp_log_file: Path) -> None:
    parser = Parser(default_line_regex_pattern, open(temp_log_file, encoding="utf-8"))
    entries_info, total_info = parser.get_entries_info()

    assert "/api/v2/banner/25019354" in entries_info
    assert len(entries_info["/api/v2/banner/25019354"]) == 2
    assert entries_info["/api/v2/banner/25019354"] == [0.39, 0.2]

    assert total_info["entries"] == 2
    assert total_info["request_time"] == (0.39 + 0.2)
