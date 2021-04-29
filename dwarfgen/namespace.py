import json
from .structure import Structure

class Namespace:
    def __init__(self, name:str):
        self.name:str = name
        self.namespaces:dict[str, Namespace] = {}
        self.structures:dict[str, Structure] = {}

    def add_and_return_namespace(self, name:str):
        self.namespaces[name] = Namespace(name)
        return self.namespaces[name]

    def add_and_return_structure(self, name:str, size:int):
        self.structures[name] = Structure(name, size)
        return self.structures[name]

    def to_json(self, json:json):
        json['namespaces'] = self.obj_to_json(json, self.namespaces)
        json['structures'] = self.obj_to_json(json, self.structures)

    def obj_to_json(self, json:json, obj:dict[str, any]) -> dict[str, json]:
        out_obj = {}
        for key, value in obj.items():
            out_obj[key] = {}
            value.to_json(out_obj[key])
        return out_obj

