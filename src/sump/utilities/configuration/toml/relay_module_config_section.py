#! /usr/bin/python3

from sump.utilities.configuration.toml.gpio_config_section_base import GPIOConfigSectionBase

class RelayModuleConfigSection(GPIOConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "RelayModule")
    
    @property
    def gpio_pins(self):
        return self.toml_config.get(self.config_section).get("gpio_pins")