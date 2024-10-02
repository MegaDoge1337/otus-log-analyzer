import gzip
import os
import re
from abc import ABC, abstractmethod
from typing import IO, Optional, Tuple


class BaseLogFileManager(ABC):
    @abstractmethod
    def search_latest_log_file(self):
        pass

    @abstractmethod
    def open_log_file(self):
        pass


class LogFileManager(ABC):
    def __init__(self, name_regex_pattern: str, log_dir_path: str) -> None:
        self.__name_regex_pattern = name_regex_pattern
        self.__log_dir_path = log_dir_path

    def search_latest_log_file(self) -> Optional[Tuple[str, str]]:
        if not os.path.exists(self.__log_dir_path):
            print(f"Directory {self.__log_dir_path} does not exists")
            return None

        logs_list = os.listdir(self.__log_dir_path)
        latest_date = "00000000"
        latest_log = ""

        for log_name in logs_list:
            name_match = re.search(self.__name_regex_pattern, log_name)
            if name_match:
                date = name_match.group("date")
                if date > latest_date:
                    latest_date = date
                    latest_log = log_name

        if latest_log == "":
            return None

        return latest_log, latest_date

    def open_log_file(self, log_path: str) -> Tuple[IO[str], str]:
        if ".gz" in log_path:
            return gzip.open(log_path, mode="rt", encoding="utf-8"), ".gz"

        return open(log_path, encoding="utf-8"), ".log"
