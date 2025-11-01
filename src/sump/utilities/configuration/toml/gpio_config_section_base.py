#! /usr/bin/python3

from utilities.configuration.toml.config_section_base import ConfigSectionBase

class GPIOConfigSectionBase(ConfigSectionBase):
    def __init__(self, toml_config, section_name) -> None:
        super().__init__(toml_config, section_name)
    
    @property
    def gpio_mode(self):
        return int(self.toml_config.get(self.config_section).get("gpio_mode"))