import json
from typing import Dict, List, Union

import pytest

from src.app.config_manager import ConfigManager


@pytest.fixture()
def default_config() -> Dict[str, Union[str, int]]:
    return {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
    }


@pytest.fixture()
def external_config() -> Dict[str, Union[str, int]]:
    return {
        "REPORT_SIZE": 500,
        "REPORT_DIR": "./another_reports",
        "LOG_DIR": "./another_log",
        "PARAM": "value",
    }


@pytest.fixture()
def argv_with_config(tmp_path) -> List[str]:

    external_config_json = json.dumps(
        {
            "REPORT_SIZE": 500,
            "REPORT_DIR": "./another_reports",
            "LOG_DIR": "./another_log",
            "PARAM": "value",
        }
    )

    external_config_file = tmp_path / "config.json"
    external_config_file.write_text(external_config_json)

    return ["main.py", "--config", str(external_config_file)]


@pytest.fixture()
def argv_without_config() -> List[str]:
    return ["main.py", "--other-args"]


@pytest.fixture()
def argv_without_config_path() -> List[str]:
    return ["main.py", "--config"]


def test_is_external_config_defined(
    argv_with_config: List[str], argv_without_config: List[str]
) -> None:
    config_manager = ConfigManager({})

    assert config_manager.is_external_config_defined(argv_with_config)
    assert not config_manager.is_external_config_defined(argv_without_config)


def test_get_external_config_path(
    argv_with_config: List[str],
    argv_without_config: List[str],
    argv_without_config_path: List[str],
) -> None:
    config_manager = ConfigManager({})

    assert (
        config_manager.get_external_config_path(argv_with_config) == argv_with_config[2]
    )
    assert config_manager.get_external_config_path(argv_without_config) is None
    assert config_manager.get_external_config_path(argv_without_config_path) is None


def test_apply_external_config_with_config(
    argv_with_config: List[str],
    default_config: Dict[str, Union[str, int]],
) -> None:
    config_manager = ConfigManager(default_config)
    config = config_manager.apply_external_config(argv_with_config)

    assert config["REPORT_SIZE"] == 500
    assert config["REPORT_DIR"] == "./another_reports"
    assert config["LOG_DIR"] == "./another_log"
    assert "PARAM" not in config


def test_apply_external_config_without_config(
    argv_without_config: List[str],
    default_config: Dict[str, Union[str, int]],
) -> None:
    config_manager = ConfigManager(default_config)
    config = config_manager.apply_external_config(argv_without_config)

    assert config["REPORT_SIZE"] == 1000
    assert config["REPORT_DIR"] == "./reports"
    assert config["LOG_DIR"] == "./log"


def test_apply_external_config_without_config_path(
    argv_without_config_path: List[str],
    default_config: Dict[str, Union[str, int]],
) -> None:
    config_manager = ConfigManager(default_config)
    config = config_manager.apply_external_config(argv_without_config_path)

    assert config["REPORT_SIZE"] == 1000
    assert config["REPORT_DIR"] == "./reports"
    assert config["LOG_DIR"] == "./log"
