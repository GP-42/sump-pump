# Services

## How to create the service files

1. Install the project in editable mode using the command ```pip install -e .``` when you're in the project root folder (```sump-pump```).
2. Make sure you provided values for the following entries in the ```.env``` file:  
    - ServicePathToPython  
      *path where Python is installed*  
      something like ```/usr/bin/python3```
    - ServiceWorkingDir  
      *path where the Python scripts are located*  
      something like ```/home/myUser/sump-pump/src/sump``` for this project
3. Generate the service files by executing the Python script ```sump-pump/scripts/create_service_files.py```.
4. The service files are created in the folder ```sump-pump/services```.
  
> [!IMPORTANT]
> The command ```systemctl``` requires elevated privileges. You have to do either of the following:
> - precede every single call with ```sudo```
> - switch to an interactive login shell with root privileges using ```sudo -i```
  
## Install the service files on RPi

1. Copy the generated service files to the Systemd services folder: ```/lib/systemd/user```. (Adjust any file permissions of the generated service files if required.)
2. Reload Systemd: ```systemctl --user daemon-reload```.

## Testing the services

1. To start all the services you only need to start the service for the buttons. The dependencies will automatically start the other services.  
```systemctl --user start mqtt-sump-buttons```
2. To stop all the services you only need to stop the service for the processor. The dependencies will automatically stop the other services.  
```systemctl --user stop mqtt-sump-processor```

## Automatically start the services on startup

1. Enable each service using this command: ```systemctl --user enable <service name>```.
2. Congratulations! The services will now automatically run on startup.
