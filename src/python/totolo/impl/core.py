from collections import OrderedDict
from copy import deepcopy


class TOAttr:
    def __init__(self, datatype="blob", default="", required=False):
        self.datatype = datatype
        self.default = default
        self.required = required


class TOObjectMeta(type):
    def __new__(meta, name, bases, attr):
        to_attrs = []
        for base in bases:
            for key, value in getattr(base, "_to_attrs", []):
                if key not in attr:
                    to_attrs.append(key, value)
        for key, value in list(attr.items()):
            if isinstance(value, TOAttr):
                to_attrs.append((key, value))
                del attr[key]
        attr["_to_attrs"] = to_attrs
        return super().__new__(meta, name, bases, attr)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        for key, value in self._to_attrs:
            if not hasattr(self, key):
                setattr(self, key, deepcopy(value.default))
        return self

    @classmethod
    def __prepare__(mcls, _cls, _bases):
        return OrderedDict()


def to(*args, **kwargs):
    return TOAttr(*args, **kwargs)


class TOObject(metaclass=TOObjectMeta):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def iter_attrs(self):
        pass
