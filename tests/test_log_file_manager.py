from pathlib import Path

import pytest

from src.app.log_file_manager import LogFileManager


@pytest.fixture
def default_name_regex_pattern() -> str:
    return r"^nginx-access-ui\.log-(?P<date>\d{8})(?:\.gz)?$"


@pytest.fixture
def temp_log_files_dir(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp("test_logs")

    tmp_nginx_gz_access_ui = temp_dir / "nginx-access-ui.log-20170630.gz"
    tmp_nginx_gz_access_ui.write_text("nginx-access-ui.log-20170630.gz")

    tmp_nginx_bz2_access_ui = temp_dir / "nginx-access-ui.log-20170830.bz2"
    tmp_nginx_bz2_access_ui.write_text("nginx-access-ui.log-20170830.bz2")

    tmp_nginx_txt_access_ui = temp_dir / "nginx-access-ui.log-20180630.txt"
    tmp_nginx_txt_access_ui.write_text("nginx-access-ui.log-20180630.txt")

    tmp_apache_log_access_service = temp_dir / "nginx-access-service.log-20170630.gz"
    tmp_apache_log_access_service.write_text("nginx-access-service.log-20170630.gz")

    tmp_apache_log_access_ui = temp_dir / "apache-access-ui.log-20200530.txt"
    tmp_apache_log_access_ui.write_text("apache-access-ui.log-20200530.txt")

    tmp_log_access_ui = temp_dir / "access_ui-20240120.txt"
    tmp_log_access_ui.write_text("access_ui-20240120.txt")

    return temp_dir


@pytest.fixture
def temp_log_files_dir_empty(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp("test_logs")
    return temp_dir


@pytest.fixture
def temp_log_files_dir_only_gz(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp("test_logs")

    tmp_nginx_gz_access_ui = temp_dir / "nginx-access-ui.log-20170630.gz"
    tmp_nginx_gz_access_ui.write_text("nginx-access-ui.log-20170630.gz")

    return temp_dir


@pytest.fixture
def temp_log_files_dir_only_log(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp("test_logs")

    tmp_nginx_gz_access_ui = temp_dir / "nginx-access-ui.log-20170630"
    tmp_nginx_gz_access_ui.write_text("nginx-access-ui.log-20170630")

    return temp_dir


def test_search_latest_log_file(
    temp_log_files_dir: Path, default_name_regex_pattern: str
) -> None:
    log_dir_path = str(temp_log_files_dir)
    log_file_manager = LogFileManager(default_name_regex_pattern, log_dir_path)

    assert log_file_manager.search_latest_log_file() == (
        "nginx-access-ui.log-20170630.gz",
        "20170630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-ui.log-20170830.bz2",
        "20170830",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-ui.log-20180630.txt",
        "20180630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-service.log-20170630.gz",
        "20170630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "apache-access-ui.log-20200530.txt",
        "20200530",
    )
    assert log_file_manager.search_latest_log_file() != (
        "access_ui-20240120.txt",
        "20240120",
    )


def test_search_latest_log_file_dir_empty(
    temp_log_files_dir_empty: Path, default_name_regex_pattern: str
) -> None:
    log_dir_path = str(temp_log_files_dir_empty)
    log_file_manager = LogFileManager(default_name_regex_pattern, log_dir_path)

    assert log_file_manager.search_latest_log_file() is None
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-ui.log-20170630.gz",
        "20170630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-ui.log-20170830.bz2",
        "20170830",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-ui.log-20180630.txt",
        "20180630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "nginx-access-service.log-20170630.gz",
        "20170630",
    )
    assert log_file_manager.search_latest_log_file() != (
        "apache-access-ui.log-20200530.txt",
        "20200530",
    )
    assert log_file_manager.search_latest_log_file() != (
        "access_ui-20240120.txt",
        "20240120",
    )


def test_open_latest_log_file_extention_gz(
    temp_log_files_dir_only_gz: Path, default_name_regex_pattern: str
) -> None:
    log_dir_path = str(temp_log_files_dir)
    log_file_manager = LogFileManager(default_name_regex_pattern, log_dir_path)
    latest_log_path = str(
        temp_log_files_dir_only_gz / "nginx-access-ui.log-20170630.gz"
    )

    assert log_file_manager.open_log_file(latest_log_path) is not None
    assert log_file_manager.open_log_file(latest_log_path)[1] != ".log"
    assert log_file_manager.open_log_file(latest_log_path)[1] == ".gz"


def test_open_latest_log_file_extention_log(
    temp_log_files_dir_only_log: Path, default_name_regex_pattern: str
) -> None:
    log_dir_path = str(temp_log_files_dir_only_log)
    log_file_manager = LogFileManager(default_name_regex_pattern, log_dir_path)
    latest_log_path = str(temp_log_files_dir_only_log / "nginx-access-ui.log-20170630")

    assert log_file_manager.open_log_file(latest_log_path) is not None
    assert log_file_manager.open_log_file(latest_log_path)[1] != ".gz"
    assert log_file_manager.open_log_file(latest_log_path)[1] == ".log"
