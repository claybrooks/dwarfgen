import json
from .member import Member

class BaseStructure:
    def __init__(self, type_offset, accessibility, byte_offset):
        self.type_offset = type_offset
        self.accessibility = accessibility
        self.byte_offset = byte_offset
        self.type = None

class Structure:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.template_params = []
        self.base_structures = {}
        self.members = {}

    def create_member(self, name, type_offset):
        self.members[name] = Member(name, type_offset)
        return self.members[name]

    def add_base_structure(self, type_offset, accessibility, byte_offset):
        self.base_structures[type_offset] = BaseStructure(type_offset, accessibility, byte_offset)

    def to_json(self, json):
        json['byteSize'] = self.size

        member_members = {k:v for k,v in self.members.items() if not v.is_static}
        static_members = {k:v for k,v in self.members.items() if v.is_static}

        if member_members != {}:
            json['members'] = self.obj_to_json(json, member_members)
        if static_members != {}:
            json['staticMembers'] = self.obj_to_json(json, static_members)

        if self.base_structures != {}:
            json['baseStructures'] = {}
            baseStructures = json['baseStructures']
            for base_structure in self.base_structures.values():
                baseStructures[base_structure.type] = {
                    'type': base_structure.type,
                    'byteOffset': base_structure.byte_offset,
                    'accessibility': base_structure.accessibility
                }

    def obj_to_json(self, json, obj):
        if obj == {}:
            return

        out_obj = {}
        for key, value in obj.items():
            out_obj[key] = {}
            value.to_json(out_obj[key])
        return out_obj
