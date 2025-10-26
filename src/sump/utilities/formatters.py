#! /usr/bin/python3

from datetime import datetime

def get_formatted_now() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f")