#! /usr/bin/python3

class ServiceConfiguration():
    def __init__(self, config) -> None:
        self.config = config
    
    @property
    def User(self):
        return self.config["ServiceUser"]
    
    @property
    def PathToPython(self):
        return self.config["ServicePathToPython"]
    
    @property
    def WorkingDir(self):
        return self.config["ServiceWorkingDir"]