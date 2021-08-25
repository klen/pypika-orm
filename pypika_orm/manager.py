import typing as t

from aio_databases import Database
from pypika.enums import Dialects

from .model import Model
from .query import ModelQueryBuilder
from .dialects import DIALECT_TO_BUILDER


_dialects = {
    'sqlite': 'sqllite',
    'postgres': 'postgressql',
    'postgresql': 'postgressql',
}


class Manager:
    """Manage database and models."""

    db: t.Optional[Database] = None
    dialect: t.Optional[Dialects] = None

    def __init__(self, database: t.Union[Database, str] = None, *, dialect: str = None):
        """Initialize dialect and database."""
        if dialect:
            self.dialect = Dialects(_dialects.get(dialect, dialect))

        if database:
            if isinstance(database, str):
                database = Database(database)

            self.db = database
            self.dialect = Dialects(_dialects.get(database.backend.name, database.backend.name))

    def __call__(self, model: Model, **kwargs) -> ModelQueryBuilder:
        """Create a query builder."""
        builder_cls = DIALECT_TO_BUILDER.get(self.dialect, ModelQueryBuilder)
        if builder_cls is ModelQueryBuilder:
            kwargs['dialect'] = self.dialect
        return builder_cls(model, db=self.db, **kwargs)

    async def __aenter__(self):
        """Init database."""
        assert self.db, 'DB is not initialized'
        await self.db.__aenter__()
        return self

    def __aexit__(self, *args):
        """Close database."""
        assert self.db, 'DB is not initialized'
        return self.db.__aexit__(*args)

    def __getattr__(self, name: str):
        """Proxy self methods."""
        assert self.db, 'DB is not initialized'
        return getattr(self.db, name)

    def __str__(self) -> str:
        if self.db:
            return self.db.url

        if self.dialect:
            return self.dialect.value

        return ''

    def __repr__(self) -> str:
        return f"<Manager {self}>"
