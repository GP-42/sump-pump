#! /usr/bin/python3

class MQTTCredentials():
    def __init__(self, module_name : str, config) -> None:
        self.module = module_name
        self.config = config
    
    @property
    def MQTTUser(self):
        return self.config[f"MQTTUser{self.module}"]
    
    @property
    def MQTTPassword(self):
        return self.config[f"MQTTPassword{self.module}"]