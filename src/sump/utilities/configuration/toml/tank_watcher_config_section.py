#! /usr/bin/python3

from utilities.configuration.toml.config_section_base import ConfigSectionBase

class TankWatcherConfigSection(ConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "TankWatcher")
    
    @property
    def sensor_height(self):
        return float(self.toml_config.get(self.config_section).get("sensor_height"))