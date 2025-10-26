#! /usr/bin/python3

from enum import Enum, Flag

import json
import typing

class InferGenericBase[T]():
    _class: typing.Type[T]

    def get_my_type(self, *args, **kwargs) -> T:
        return self._class(*args, **kwargs)

class GenericJSONEncoder[T](InferGenericBase, json.JSONEncoder):
    def default(self, o):
        if o.__dict__.keys() == self.get_my_type().__dict__.keys():
            return o.__dict__
        elif isinstance(o, Enum) or isinstance(o, Flag):
            return o.name
        else:
            return super().default(o)

class GenericJSONDecoder[T](InferGenericBase, json.JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs) -> None:
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        object_keys = o.keys()
        if object_keys == self.get_my_type().__dict__.keys():
            arg_list = []
            for key in object_keys:
                arg_list.append(o.get(key))
            
            decoded_class = self.get_my_type(*tuple(arg_list))
            
            return decoded_class
        else:
            raise TypeError(f"JSON string does not match object {self.get_my_type().__class__.__name__}")