import json

class Member:
    def __init__(self, name, type_offset, byte_offset):
        self.name = name
        self.type_offset    = type_offset
        self.byte_offset    = byte_offset
        self.bit_offset     = None
        self.bit_size       = None
        self.byte_size      = None
        self.type_str       = None
        self.upper_bound    = None
        self.lower_bound    = None

    def to_json(self, json):
        json['byteOffset'] = self.byte_offset

        if self.bit_offset:
            json['bitOffset'] = self.bit_offset

        if self.bit_size is not None:
            json['bitSize'] = self.bit_size

        if self.byte_size is not None:
            json['byteSize'] = self.byte_size

        if self.type_str is not None:
            json['type'] = self.type_str

        if self.upper_bound is not None:
            json['upperBound'] = self.upper_bound

        if self.lower_bound is not None:
            json['lowerBound'] = self.lower_bound
