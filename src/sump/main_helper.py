#! /usr/bin/python3

from filelock import FileLock, Timeout
from sump.utilities.files import open_utf8
from sump.utilities.formatters import get_formatted_now

import os
import signal
import traceback

class MainHelper():
    def __init__(self, file_path_py) -> None:
        signal.signal(signal.SIGHUP, self.exit_handler)
        signal.signal(signal.SIGTERM, self.exit_handler)

        self.file_path = file_path_py.replace(".py", "_check.txt")
        self.lock_path = f"{self.file_path}.lock"
        self.error_raised = False
        self.lock = None
        self.cleaned_up = False
    
    def _perform_cleanup(self):
        if not self.error_raised:
            if not self.cleaned_up:
                with self.lock:
                    with open_utf8(self.file_path, "a") as file:
                        file.write(f"\nEnd: {get_formatted_now()}")
                
                self.cleaned_up = True
            
            if os.path.exists(self.lock_path):
                os.remove(self.lock_path)
    
    def exit_handler(self, signum, frame):
        self._perform_cleanup()

    def run(self, MQTTSumpController):
        try:
            self.lock = FileLock(self.lock_path, thread_local=False, timeout=0)
            
            try:
                with self.lock:
                    print("Lock activated.")
                    with open_utf8(self.file_path, "w") as file:
                        file.write(f"Start: {get_formatted_now()}")
                        
                    MQTTSumpController().start()
            except Timeout:
                self.error_raised = True
                print("Process already running. Quitting.")
            finally:
                self._perform_cleanup()
        except Exception as e:
            traceback.print_exc()