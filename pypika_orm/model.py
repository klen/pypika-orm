import typing as t

from pypika.queries import Table, Selectable

from .fields import Field


class ModelOptions:
    """Prepare options for an model."""

    table_name: str = ''
    primary_key: t.Optional[t.List[str]] = None
    foreign_keys: t.Optional[t.Dict[str, Field]] = None

    def __init__(self, cls):
        """Inherit meta options."""
        for base in reversed(cls.mro()):
            if hasattr(base, "Meta"):
                for k, v in base.Meta.__dict__.items():
                    if not k.startswith('_'):
                        setattr(self, k, v)

        self.setup(cls)

    def setup(self, cls):
        """Setup the options."""
        cls.meta = self

        self.table_name = self.table_name or cls.__name__.lower()
        self.table = Table(self.table_name)  # TODO: do we need it?
        self.foreign_keys = {}

        self.fields = {}
        for name in vars(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Field):
                attr.bind(cls, name)

        if not getattr(self, 'primary_key', None) and self.fields:
            self.primary_key = list(self.fields.keys())[0],


class Model(Selectable):
    """Base model class."""

    def __init__(self, **kwargs):
        """Initialize the model."""
        for name, field in self.meta.fields.items():
            value = kwargs.get(name, None if field.default is None else field.default)
            setattr(self, name, value)

    def __init_subclass__(cls, **kwargs):
        ModelOptions(cls)
        return cls

    def __str__(self):
        return ','.join(f"{getattr(self, pk)}" for pk in self.meta.primary_key)

    def __repr__(self):
        model = type(self).__name__
        return f"<{model} {self}>"

    @classmethod
    def get_sql(cls, **kwargs: t.Any) -> str:
        return cls.meta.table.get_sql(**kwargs)
