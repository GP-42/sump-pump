#! /usr/bin/python3

from sump.utilities.singleton import ThreadSafeSingletonMeta

class ConfigurationBase(metaclass=ThreadSafeSingletonMeta):
    config = None

    def __init__(self) -> None:
        if self.config is None:
            self.reload()
    
    def reload(self):
        pass