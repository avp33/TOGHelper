"""Module containing utility functions for the bot."""
import json

class JSONSerializable(object):
    """
    Represents a class that can be deserialized to an object by calling
    from_json_dict
    """
    @staticmethod
    def from_json_dict(**kwargs):
        raise ValueError('Implement in subclasses')


def convert_to_json_str(obj: object):
    """Recursively converts the given object to a json string, returning the result"""
    return json.dumps(json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    ))


def convert_json_to_object(json_str: str, cls: JSONSerializable.__class__):
    """Converts the given json string to an object of the given class"""
    json_dict = json.loads(json_str)
    return cls.from_json_dict(**json_dict)