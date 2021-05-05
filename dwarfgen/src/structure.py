import json
from .member import Member

class Structure:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.template_params = []
        self.members = {}

    def create_member(self, name, type_offset):
        self.members[name] = Member(name, type_offset)
        return self.members[name]

    def to_json(self, json):
        json['byteSize'] = self.size

        member_members = {k:v for k,v in self.members.items() if not v.is_static}
        static_members = {k:v for k,v in self.members.items() if v.is_static}

        if member_members != {}:
            json['members'] = self.obj_to_json(json, member_members)
        if static_members != {}:
            json['staticMembers'] = self.obj_to_json(json, static_members)

    def obj_to_json(self, json, obj):
        if obj == {}:
            return

        out_obj = {}
        for key, value in obj.items():
            out_obj[key] = {}
            value.to_json(out_obj[key])
        return out_obj
