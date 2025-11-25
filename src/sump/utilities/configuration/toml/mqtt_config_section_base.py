#! /usr/bin/python3

from sump.utilities.configuration.toml.config_section_base import ConfigSectionBase

class MQTTConfigSectionBase(ConfigSectionBase):
    def __init__(self, toml_config, section_name) -> None:
        super().__init__(toml_config, section_name)
    
    @property
    def host(self):
        return self.toml_config.get(self.config_section).get("host")
    
    @property
    def port(self):
        return int(self.toml_config.get(self.config_section).get("port"))
    
    @property
    def client_id(self):
        return self.toml_config.get(self.config_section).get("client_id")
    
    @property
    def message_qos(self):
        return int(self.toml_config.get(self.config_section).get("message_qos"))