import json
from .structure import Structure
from .enumeration import Enumeration
from .union import Union

class Namespace:
    def __init__(self, name):
        self.name = name
        self.namespaces = {}
        self.structures = {}
        self.enumerations = {}
        self.unions = {}

    def create_namespace(self, name):
        if name not in self.namespaces:
            self.namespaces[name] = Namespace(name)
        return self.namespaces[name]

    def create_structure(self, name, size):
        if name not in self.structures:
            self.structures[name] = Structure(name, size)
        return self.structures[name]

    def create_enumeration(self, name, size, type, encoding):
        if name not in self.enumerations:
            self.enumerations[name] = Enumeration(name, size, type, encoding)
        return self.enumerations[name]

    def create_union(self, name, size):
        if name not in self.unions:
            self.unions[name] = Union(name, size)
        return self.unions[name]

    def to_json(self, json):
        json['namespaces'] = self.obj_to_json(json, self.namespaces)
        json['structures'] = self.obj_to_json(json, self.structures)
        json['enumerations'] = self.obj_to_json(json, self.enumerations)
        json['unions'] = self.obj_to_json(json, self.unions)

    def obj_to_json(self, json, obj):
        out_obj = {}
        for key, value in obj.items():
            out_obj[key] = {}
            value.to_json(out_obj[key])
        return out_obj

