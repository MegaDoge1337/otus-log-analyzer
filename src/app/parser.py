import re
from abc import ABC, abstractmethod
from typing import IO, Dict, Generator, Tuple, Union


class BaseParser(ABC):
    @abstractmethod
    def parse_log_entries(self) -> Generator[Dict[str, str], None, None]:
        pass

    @abstractmethod
    def get_entries_info(
        self,
    ) -> Tuple[Dict[str, list[float]], Dict[str, Union[int, float]]]:
        pass


class Parser(BaseParser):
    def __init__(self, line_regex_pattern: str, log_file: IO[str]) -> None:
        self.__line_regex_pattern = line_regex_pattern
        self.__log_file = log_file

    def parse_log_entries(self) -> Generator[Dict[str, str], None, None]:
        idx = 0
        for line in self.__log_file:
            idx += 1
            line_match = re.search(self.__line_regex_pattern, line)

            if line_match is None:
                yield {
                    "error": f"Failed parsing {self.__log_file.name} line {idx} `{line}` does not contains format matches"
                }

                continue

            yield line_match.groupdict()

    def get_entries_info(
        self,
    ) -> Tuple[Dict[str, list[float]], Dict[str, Union[int, float]]]:
        entries_info: Dict[str, list[float]] = {}
        total_info = {"entries": 0, "request_time": 0.0}

        for entry in self.parse_log_entries():
            if "error" in entry:
                print(entry)
                continue

            url = entry["url"]
            request_time = float(entry["request_time"])

            if url not in entries_info:
                entries_info[url] = []

            entries_info[url].append(request_time)

            total_info["entries"] += 1
            total_info["request_time"] += request_time

        return entries_info, total_info
