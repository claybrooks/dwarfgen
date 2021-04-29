import json
from .member import Member

class Structure:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.members = {}

    def add_and_return_member(self, name, type_offset, byte_offset):
        self.members[name] = Member(name, type_offset, byte_offset)
        return self.members[name]

    def to_json(self, json):
        json['size'] = self.size
        json['members'] = self.obj_to_json(json, self.members)

    def obj_to_json(self, json, obj):
        out_obj = {}
        for key, value in obj.items():
            out_obj[key] = {}
            value.to_json(out_obj[key])
        return out_obj
