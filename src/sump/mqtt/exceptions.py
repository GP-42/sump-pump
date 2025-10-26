#! /usr/bin/python3

class InvalidTopicError(Exception):
    def __init__(self, topic) -> None:            
        super().__init__(f"Invalid topic passed: {topic}")