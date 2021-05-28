import json
from .member import Member


class Enumeration:
    def __init__(self, name, size, type, encoding):
        self.name = name
        self.size = size
        self.type = type
        self.encoding = encoding
        self.values = []
        self.type_str = None

    def add_value(self, name, const_value):
        self.values.append((name, const_value))

    def to_json(self, json):
        json['byteSize'] = self.size
        json['type'] = self.type_str

        json['values'] = {}
        values = json['values']

        for pair in self.values:
            name, const_value = pair
            values[name] = const_value
