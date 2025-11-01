#! /usr/bin/python3

from utilities.configuration.toml.gpio_config_section_base import GPIOConfigSectionBase

class Hcsr04SensorConfigSection(GPIOConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "Hcsr04Sensor")
    
    @property
    def gpio_trigger_pin(self):
        return int(self.toml_config.get(self.config_section).get("gpio_trigger_pin"))
    
    @property
    def gpio_echo_pin(self):
        return int(self.toml_config.get(self.config_section).get("gpio_echo_pin"))