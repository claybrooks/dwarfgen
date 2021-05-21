import json

class BoundsList:
    def __init__(self, index, lower, upper):
        self.index = index
        self.lower = lower
        self.upper = upper

    def get_json(self):
        return {
            'index': self.index,
            'lowerBound': self.lower,
            'upperBound': self.upper
        }

class Member:
    def __init__(self, name, type_offset):
        self.name           = name
        self.type_offset    = type_offset
        self.byte_offset    = None
        self.bit_offset     = None
        self.bit_size       = None
        self.byte_size      = None
        self.type_str       = None
        self.upper_bound    = None
        self.lower_bound    = None
        self.bounds_list    = None
        self.accessibility  = None
        self.min_val        = None
        self.max_val        = None
        self.is_static      = False

    def add_to_bounds_list(self, lower, upper):
        if self.bounds_list is None:
            self.bounds_list = []

        self.bounds_list.append(BoundsList(len(self.bounds_list), lower, upper))

    def to_json(self, json):

        if self.type_str is not None:
            json['type'] = self.type_str

        if self.accessibility is not None:
            json['accessibility'] = self.accessibility

        if self.is_static:
            return

        if self.byte_offset is not None:
            json['byteOffset'] = self.byte_offset

        if self.bit_offset is not None:
            json['bitOffset'] = self.bit_offset

        if self.bit_size is not None:
            json['bitSize'] = self.bit_size

        if self.byte_size is not None:
            json['byteSize'] = self.byte_size

        if self.upper_bound is not None:
            json['upperBound'] = self.upper_bound

        if self.lower_bound is not None:
            json['lowerBound'] = self.lower_bound

        if self.bounds_list is not None:
            json['bounds'] = []
            for bound in self.bounds_list:
                json['bounds'].append(bound.get_json())

        if self.min_val is not None:
            json['minVal'] = self.min_val

        if self.max_val is not None:
            json['maxVal'] = self.max_val
