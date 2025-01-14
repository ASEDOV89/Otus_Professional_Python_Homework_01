import datetime
import gzip
import logging
from unittest.mock import patch

import pytest

from src.analyzer.config import load_config, parse_args
from src.analyzer.file_utils import find_latest_log, open_log_file
from src.analyzer.log import get_logger


def test_load_config_missing_file(tmp_path):
    with pytest.raises(SystemExit):
        load_config(tmp_path / "nonexistent.json")


def test_load_config_invalid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("This is not valid JSON")
    with pytest.raises(SystemExit):
        load_config(config_file)


def test_load_config_valid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"key": "value"}')
    config = load_config(config_file)
    assert config == {"key": "value"}


def test_parse_args_default_config():
    args = parse_args()
    assert args.config == "config/config.json"


@pytest.fixture
def log_dir(tmp_path):
    log_files = [
        "nginx-access-ui.log-20200101.gz",
        "nginx-access-ui.log-20200102.gz",
        "nginx-access-ui.log-20200103.gz",
    ]
    for file_name in log_files:
        file_path = tmp_path / file_name
        with gzip.open(file_path, "wt") as f:
            f.write("log file content\n")
    return tmp_path


def test_find_latest_log(log_dir):
    latest_log, latest_date = find_latest_log(log_dir)
    assert latest_log == "nginx-access-ui.log-20200103.gz"
    assert latest_date == datetime.date(2020, 1, 3)


def test_find_latest_log_no_logs(tmp_path):
    latest_log, latest_date = find_latest_log(tmp_path)
    assert latest_log is None
    assert latest_date is None


def test_open_log_file_gzip(log_dir):
    log_path = log_dir / "nginx-access-ui.log-20200101.gz"
    with open_log_file(log_path) as f:
        content = f.read()
    assert content == "log file content\n"


def test_open_log_file_plain_text(log_dir):
    log_path = log_dir / "nginx-access-ui.log-20200101"
    log_path.write_text("plain text log file content")
    with open_log_file(log_path) as f:
        content = f.read()
    assert content == "plain text log file content"


@pytest.fixture
def logger_config():
    return {"LOG_FILE": None}


def test_get_logger_no_log_file(logger_config):
    with patch("logging.basicConfig") as mock_basicConfig:
        logger = get_logger(logger_config)
        mock_basicConfig.assert_called_once()
        assert logger is not None
        assert logging.getLogger().handlers[0].formatter._fmt == "%(message)s"


def test_get_logger_with_log_file(tmp_path, logger_config):
    log_file = tmp_path / "test.log"
    logger_config["LOG_FILE"] = str(log_file)
    with patch("logging.FileHandler") as mock_FileHandler:
        logger = get_logger(logger_config)
        mock_FileHandler.assert_called_once_with(str(log_file))
        assert logger is not None
