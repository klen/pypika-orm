from __future__ import annotations

import typing as t

import datetime
import decimal

from pypika.queries import Field as _Field


if t.TYPE_CHECKING:
    from .model import Model


class FieldMeta(type):

    py_type: t.Type

    def __new__(mcs, name: str, bases: t.Tuple[t.Type, ...], attrs: dict):
        if len(bases) > 1 and issubclass(bases[0], Field):
            base, *types = bases
            attrs['py_type'] = types[0] if len(types) == 1 else t.Union[types]
            cls = super(FieldMeta, mcs).__new__(mcs, name, (base,), attrs)
            return cls

        return super(FieldMeta, mcs).__new__(mcs, name, bases, attrs)


class FieldAccessor:

    def __init__(self, name: str, field: Field):
        self.name = name
        self.field = field

    def __get__(self, model, instance_type=None):
        if model is not None:
            return model.__data__.get(self.name)
        return self.field

    def __set__(self, model, value):
        model.__data__[self.name] = value
        model.__dirty__.add(self.name)


class Field(_Field, metaclass=FieldMeta):

    py_type: t.Type
    db_type: str

    name: str

    def __init__(self, null: bool = None, default: t.Any = None, **meta):
        self.null = null
        self.default = default
        self.meta = meta

    def bind(self, model: 'Model', name: str):
        self.name = name
        self.table = model.meta.table

        model.meta.fields[name] = self
        setattr(model, name, FieldAccessor(name, self))


class Auto(Field, int):
    db_type = 'INTEGER'


class BigAuto(Field, int):
    db_type = 'BIGINT'


class BigInt(Field, int):
    db_type = 'BIGINT'


class Blob(Field, bytes):
    db_type = 'BLOB'


class Bool(Field, int):
    db_type = 'SMALLINT'


class Char(Field, str):
    db_type = 'CHAR'


class Date(Field, datetime.date):
    db_type = 'DATE'


class Datetime(Field, datetime.datetime):
    db_type = 'DATETIME'


class Decimal(Field, decimal.Decimal):
    db_type = 'DECIMAL'


class Double(Field, float):
    db_type = 'REAL'


class Float(Field, float):
    db_type = 'REAL'


class Integer(Field, int):
    db_type = 'INTEGER'


class SmallInt(Field, int):
    db_type = 'SMALLINT'


class Text(Field, str):
    db_type = 'TEXT'


class Time(Field, datetime.time):
    db_type = 'TIME'


class UUID(Field, str):
    db_type = 'TEXT'


class UUIDB(Field, bytes):
    db_type = 'BLOB'


class Varchar(Field, str):

    def __init__(self, max_length: int = 256, **kwargs):
        self.max_length = max_length
        super(Varchar, self).__init__(**kwargs)

    @property
    def db_type(self):
        return f"VARCHAR({self.max_length})"


class ForeignKey(Field, type):

    def __init__(self, rel_field: Field, **kwargs):
        self.rel_field = rel_field
        super(ForeignKey, self).__init__(**kwargs)

    @property
    def db_type(self):
        if not isinstance(self.rel_field, Auto):
            return self.rel_field.db_type

        if isinstance(self.rel_field, BigAuto):
            return BigInt.db_type

        return Integer.db_type

    def bind(self, model: 'Model', name: str):
        super(ForeignKey, self).bind(model, name)
        model.meta.foreign_keys[name] = self
