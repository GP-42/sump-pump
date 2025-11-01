#! /usr/bin/python3

class ConfigSectionBase():
    def __init__(self, toml_config, section_name) -> None:
        self.toml_config = toml_config
        self.config_section = section_name