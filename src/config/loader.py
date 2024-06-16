"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import configparser
import logging
import pathlib
from pathlib import Path

from src.config.helper import singleton
from src.config.models import DEPRECATED_INI_KEYS, AdvancedOptionsModel, CharModel, GeneralModel

LOGGER = logging.getLogger(__name__)
PARAMS_INI = "params.ini"


@singleton
class IniConfigLoader:
    def __init__(self):
        self._advanced_options = AdvancedOptionsModel()
        self._char = CharModel()
        self._general = GeneralModel()
        self._parser = None
        self._user_dir = pathlib.Path.home() / ".d4lf"
        self._user_dir.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self, clear: bool = False):
        if not (self.user_dir / PARAMS_INI).exists() or clear:
            with open(self.user_dir / PARAMS_INI, "w", encoding="utf-8"):
                pass

        self._parser = configparser.ConfigParser()
        self._parser.read(self.user_dir / PARAMS_INI, encoding="utf-8")

        all_keys = [key for section in self._parser.sections() for key in self._parser[section]]
        deprecated_keys = [key for key in DEPRECATED_INI_KEYS if key in all_keys]
        for key in deprecated_keys:
            LOGGER.warning(f"Deprecated {key=} found in {PARAMS_INI}. Please remove this key from your config file.")
            # remove key from parser
            for section in self._parser.sections():
                if key in self._parser[section]:
                    self._parser.remove_option(section, key)

        if "advanced_options" in self._parser:
            self._advanced_options = AdvancedOptionsModel(**self._parser["advanced_options"])
        else:
            self._advanced_options = AdvancedOptionsModel()

        if "char" in self._parser:
            self._char = CharModel(**self._parser["char"])
        else:
            self._char = CharModel()

        if "general" in self._parser:
            self._general = GeneralModel(**self._parser["general"])
        else:
            self._general = GeneralModel()

    @property
    def advanced_options(self) -> AdvancedOptionsModel:
        return self._advanced_options

    @property
    def char(self) -> CharModel:
        return self._char

    @property
    def general(self) -> GeneralModel:
        return self._general

    @property
    def user_dir(self) -> Path:
        return self._user_dir

    def save_value(self, section, key, value):
        if self._parser is None:
            self.load()
        if section not in self._parser.sections():
            self._parser.add_section(section)
        self._parser.set(section, key, value)
        with open(self.user_dir / PARAMS_INI, "w", encoding="utf-8") as config_file:
            self._parser.write(config_file)


if __name__ == "__main__":
    a = IniConfigLoader()
    a.load()
    print(a)
