#! /usr/bin/python3

from dotenv import dotenv_values
from pathlib import Path
from sump.utilities.configuration.classic.mqtt_credentials import MQTTCredentials
from sump.utilities.configuration.classic.service_configuration import ServiceConfiguration
from sump.utilities.configuration.configuration_base import ConfigurationBase
from sump.utilities.files import get_project_root

class EnvConfiguration(ConfigurationBase):
    # _instance = None
    # _lock = threading.Lock()
    # config = None

    # def __new__(cls):
    #     if cls._instance is None: 
    #         with cls._lock:
    #             # Another thread could have created the instance
    #             # before we acquired the lock. So check that the
    #             # instance is still nonexistent.
    #             if not cls._instance:
    #                 cls._instance = super().__new__(cls)
    #     return cls._instance
    
    # def __init__(self) -> None:
    #     if self.config is None:
    #         self.reload()

    def __getitem__(self, key):
        value = self.config[key]
        if value.replace(".", "", 1).isnumeric():
            return float(value) if "." in value else int(value)
        else:
            return value
    
    def reload(self):
        path_to_use = f"{get_project_root(Path(__file__))}/config/.env"
        self.config = dotenv_values(dotenv_path=path_to_use)
    
    @property
    def SumpProcessorCredentials(self):
        return MQTTCredentials("SumpProcessor", self.config)
    
    @property
    def SumpStatusCredentials(self):
        return MQTTCredentials("SumpStatus", self.config)
    
    @property
    def SumpDBWriteCredentials(self):
        return MQTTCredentials("SumpDBWrite", self.config)
    
    @property
    def SumpRPiCredentials(self):
        return MQTTCredentials("SumpRPi", self.config)
    
    @property
    def SumpTankWatcherCredentials(self):
        return MQTTCredentials("SumpTankWatcher", self.config)
    
    @property
    def SumpRelayCredentials(self):
        return MQTTCredentials("SumpRelay", self.config)
    
    @property
    def SumpButtonsCredentials(self):
        return MQTTCredentials("SumpButtons", self.config)
    
    @property
    def Service(self):
        return ServiceConfiguration(self.config)