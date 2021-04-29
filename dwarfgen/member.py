import json

class Member:
    def __init__(self, name:str, type_offset:int, byte_offset:int):
        self.name:str = name
        self.type_offset:int    = type_offset
        self.byte_offset:int    = byte_offset
        self.bit_offset:int     = None
        self.bit_size:int       = None
        self.byte_size:int      = None
        self.type_str:str       = None
        self.upper_bound:int    = None

    def to_json(self, json:json):
        json['byteOffset'] = self.byte_offset

        if self.bit_offset:
            json['bitOffset'] = self.bit_offset

        if self.bit_size is not None:
            json['bitSize'] = self.bit_size

        if self.byte_size is not None:
            json['byte_size'] = self.byte_size

        if self.type_str is not None:
            json['type'] = self.type_str

        if self.upper_bound is not None:
            json['upper_bound'] = self.upper_bound
