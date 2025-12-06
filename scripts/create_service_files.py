#! /usr/bin/python3

from pathlib import Path
from sump.utilities.configuration.classic.env_configuration import EnvConfiguration
from sump.utilities.files import open_utf8, get_project_root

import re
import traceback

class ServiceFile:
    def __init__(self, file_name, unit_description, unit_predecessor, service_path_to_python, service_working_dir, service_python_file_name) -> None:
        self.file_name = file_name
        self.unit_description = unit_description
        self.unit_predecessor = unit_predecessor
        self.service_path_to_python = service_path_to_python
        self.service_working_dir = service_working_dir
        self.service_python_file_name = service_python_file_name

if __name__ == "__main__":
    try:
        EnvConfig = EnvConfiguration()
        
        services=[]
        services.append(ServiceFile("mqtt-sump-processor", "Processor", str(), EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_processor.py"))
        services.append(ServiceFile("mqtt-sump-status", "Status", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_status.py"))
        services.append(ServiceFile("mqtt-sump-db-write", "DB", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_db_write.py"))
        services.append(ServiceFile("mqtt-sump-rpi", "RPi", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_rpi.py"))
        services.append(ServiceFile("mqtt-sump-tank-watcher", "Tank Watcher", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_tank_watcher.py"))
        services.append(ServiceFile("mqtt-sump-relay", "Relay", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_relay.py"))
        services.append(ServiceFile("mqtt-sump-buttons", "Buttons", services[len(services)-1].file_name, EnvConfig.Service.PathToPython, EnvConfig.Service.WorkingDir, "main_buttons.py"))

        project_root = get_project_root(Path(__file__))
        for service in services:
            with open_utf8(f"{project_root}/services/template.service", "r") as src, open_utf8(f"{project_root}/services/{service.file_name}.service", "w") as dst:
                text = src.read()
                
                result = text.replace("{UNIT_DESCRIPTION}", service.unit_description)
                if service.unit_predecessor != str():
                    result = result.replace("{UNIT_PREDECESSOR}", service.unit_predecessor)
                result = result.replace("{SERVICE_PATH_TO_PYTHON}", service.service_path_to_python)
                result = result.replace("{SERVICE_WORKING_DIR}", service.service_working_dir)
                result = result.replace("{SERVICE_PYTHON_FILE}", service.service_python_file_name)

                if service.unit_predecessor == str():
                    result = re.sub(".*{UNIT_PREDECESSOR}.*\n?", str(), result)

                dst.write(result)
    
    except Exception as e:
        traceback.print_exc()