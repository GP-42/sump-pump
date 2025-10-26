#! /usr/bin/python3

from dotenv import dotenv_values
from utilities.singleton import ThreadSafeSingletonMeta

# import threading

class ConfigurationBase(metaclass=ThreadSafeSingletonMeta):
    config = None

    def __init__(self) -> None:
        if self.config is None:
            self.reload()
    
    def reload(self):
        pass

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
        self.config = dotenv_values(dotenv_path="../../config/.env")