#! /usr/bin/python3

import builtins  
 
def open_utf8(file, mode="r", *args, **kwargs):
    # Enforce utf-8, but allow explicit overrides
    kwargs.setdefault("encoding", "utf-8")
    return builtins.open(file, mode, *args, **kwargs)

def get_project_root(path) -> str:
    PROJECT_ROOT_FOLDER = "sump-pump"
    current_path = path

    while not str(current_path).endswith(PROJECT_ROOT_FOLDER):
        current_path = current_path.parent
    
    return current_path