import collections
import json
import copy


# A little hack that will make call 'to_json' on any non json serializable class
# So you can implement to_json to become json serializable
from dataclasses import dataclass, field
from typing import Union, Dict, Any, List, Iterator

from lazy import lazy


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = json.JSONEncoder().default
json.JSONEncoder.default = _default


def strip_json(json_values):
    """
    Remove null, empty strings and false and empty lists from JSON values
    (contents of arrays wont be affected).
    Can optimise exports of json data when fields are often blank
    """
    if isinstance(json_values, collections.Mapping):
        ret_value = {}
        for key, value in json_values.items():
            if value == '' or value is None or value is False or (isinstance(value, list) and not value):
                pass
            else:
                value = strip_json(value)
                ret_value[key] = value
        return ret_value

    if isinstance(json_values, list):
        ret_value = []
        for value in json_values:
            ret_value.append(strip_json(value))
        return ret_value
    return json_values


# These are too self-referential to define properly
# so mainly exist to document code
JsonPrimitiveType = Union[str, int, float, bool, None]
JsonObjType = Dict[JsonPrimitiveType, Any]
JsonListType = List[Any]
JsonDataType = Union[JsonListType, JsonObjType, JsonPrimitiveType]


@dataclass(frozen=True)
class JsonMessage:

    severity: str
    text: str

    @property
    def is_error(self) -> bool:
        # TODO get rid of all these hardcoded strings
        return self.severity == "error"

    @property
    def bs(self) -> str:
        if self.severity == "error":
            return "danger"
        if self.severity == "warning":
            return "warning"
        if self.severity == "info":
            return "info"
        return "info"


@dataclass(frozen=True)
class JsonMessages:

    messages: List[str] = field(default_factory=list)

    @staticmethod
    def error(message: str):
        return JsonMessages([JsonMessage(severity="error", text=message)])

    @staticmethod
    def warning(message: str):
        return JsonMessages([JsonMessage(severity="warning", text=message)])

    @staticmethod
    def info(message: str):
        return JsonMessages([JsonMessage(severity="info", text=message)])

    def __add__(self, other) -> 'JsonMessages':
        if not other:
            return self
        return JsonMessages(self.messages + other.messages)

    def __bool__(self):
        return bool(self.messages)

    def __iter__(self) -> Iterator[JsonMessage]:
        return iter(self.messages)


JSON_MESSAGES_EMPTY = JsonMessages()


class ClinVarSubmissionNotes:

    def __init__(self):
        self.errors: List[str] = list()

    def add_error(self, text):
        self.errors.append(text)


class ValidatedJson():
    """
    ValidatedJson can have a base bit of JSON that's either pure JSON, or other ValidatedJson
    Allowing validation messages to be associated with the parts that caused the problems
    """

    def __init__(self, json_data: JsonDataType, messages: JsonMessages = JSON_MESSAGES_EMPTY):
        self.json_data = json_data
        self.messages = messages

    def to_json(self) -> JsonDataType:
        return self.json_data

    def pure_json(self) -> JsonDataType:
        """
        returns dicts, lists, str, int, etc not combined with
        """
        return json.loads(json.dumps(self))

    @staticmethod
    def _traverse_messages(json_data) -> JsonMessages:
        messages = JSON_MESSAGES_EMPTY
        if isinstance(json_data, list):
            for val in json_data:
                messages += ValidatedJson._traverse_messages(val)
        elif isinstance(json_data, dict):
            for val in json_data.values():
                messages += ValidatedJson._traverse_messages(val)
        elif isinstance(json_data, ValidatedJson):
            messages += json_data.messages
            messages += ValidatedJson._traverse_messages(json_data.json_data)
        return messages

    def __setitem__(self, key, value):
        lazy.invalidate(self, 'all_messages')
        self.json_data[key] = value

    def __getitem__(self, item):
        return self.json_data[item]

    @lazy
    def all_messages(self) -> JsonMessages:
        """
        Returns messages associated to this ValidatedJson or any of its data
        Where the "messages" property will only pertain to this level
        """
        return ValidatedJson._traverse_messages(self)

    @property
    def has_errors(self) -> bool:
        return any(message.is_error for message in self.all_messages)

    def __copy__(self):
        # messages don't need deeop copy as they're immutable, data does though
        return ValidatedJson(json_data=copy.deepcopy(self.json_data), messages=self.messages)

    def __bool__(self):
        return bool(self.json_data) or bool(self.messages)