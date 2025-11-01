#! /usr/bin/python3

from utilities.configuration.toml.gpio_config_section_base import GPIOConfigSectionBase

class SumpOperationsConfigSection(GPIOConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "SumpOperations")
    
    @property
    def gpio_led_pin(self):
        return int(self.toml_config.get(self.config_section).get("gpio_led_pin"))
    
    @property
    def gpio_button_pin(self):
        return int(self.toml_config.get(self.config_section).get("gpio_button_pin"))