import json
from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseConfigManager(ABC):
    @abstractmethod
    def is_external_config_defined(self, argv: List[str]) -> bool:
        pass

    @abstractmethod
    def get_external_config_path(self, argv: List[str]) -> str:
        pass

    @abstractmethod
    def read_external_config(self, config_path: str) -> Dict[str, Union[str, int]]:
        pass

    @abstractmethod
    def merge_configs(self, external_config: Dict[str, Union[str, int]]) -> None:
        pass

    @abstractmethod
    def apply_external_config(self, argv: List[str]) -> Dict[str, Union[str, int]]:
        pass


class ConfigManager(BaseConfigManager):
    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        self.__config = config

    def is_external_config_defined(self, argv: List[str]) -> bool:
        return "--config" in argv

    def get_external_config_path(self, argv: List[str]) -> str:
        arg_key_index = argv.index("--config")
        return argv[arg_key_index + 1]

    def read_external_config(self, config_path: str) -> Dict[str, Union[str, int]]:
        file_content = open(config_path).read()
        return json.loads(file_content)

    def merge_configs(self, external_config: Dict[str, Union[str, int]]) -> None:
        default_config_keys = self.__config.keys()
        for key in default_config_keys:
            if key in external_config:
                self.__config[key] = external_config[key]

    def apply_external_config(self, argv: List[str]) -> Dict[str, Union[str, int]]:
        if self.is_external_config_defined(argv):
            external_config_path = self.get_external_config_path(argv)
            external_config = self.read_external_config(external_config_path)
            self.merge_configs(external_config)

        return self.__config
