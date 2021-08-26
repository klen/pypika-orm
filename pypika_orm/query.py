from __future__ import annotations

import typing as t
from inspect import isclass

from aio_databases import Database
from pypika.queries import (
    Column,
    CreateQueryBuilder,
    DropQueryBuilder,
    Query,
    QueryBuilder,
    Table,
    builder,
)

from .fields import Field


class ModelDBMixin:

    _db: t.Optional[Database]
    _model: t.Type[Model]

    get_sql: t.Callable[..., str]

    def __init__(self, *args, db: Database = None, **kwargs):
        self._db = db
        super(ModelDBMixin, self).__init__(*args, **kwargs)  # type: ignore

    def execute(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        return self._db.execute(sql, *args, **kwargs)

    def executemany(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        return self._db.executemany(sql, *args, **kwargs)

    async def fetchall(self, *args, **kwargs) -> t.List[Model]:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        records = await self._db.fetchall(sql, *args, **kwargs)
        return [self._model(**dict(rec.items())) for rec in records]

    async def fetchone(self, *args, **kwargs) -> t.Optional[Model]:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        rec = await self._db.fetchone(sql, *args, **kwargs)
        if rec is None:
            return rec

        return self._model(**dict(rec.items()))

    def fetchval(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        return self._db.fetchval(sql, *args, **kwargs)


class ModelBuilderMixin(ModelDBMixin):

    DB_TYPES: t.Dict[t.Type[Field], 'str'] = {}

    def __init__(self, model: t.Type[Model], **kwargs):
        self._model = model
        super().__init__(**kwargs)
        self._from = [model.meta.table]

    def select(self: QueryBuilder, *terms: t.Any) -> ModelQueryBuilder:
        if not (terms or self._selects):
            terms = self._model,

        prepared_terms = []
        for term in terms:
            if isclass(term) and issubclass(term, Model):
                prepared_terms += [f for f in term.meta.fields.values()]
            else:
                prepared_terms.append(term)

        return QueryBuilder.select(self, *prepared_terms)

    @builder
    def insert(self: QueryBuilder, *terms: t.Any, **values):
        self._insert_table = self._model
        if terms:
            return QueryBuilder.insert(self, *terms)

        if not values:
            return self

        fields = self._model.meta.fields
        values = {name: value for name, value in values.items() if name in fields}
        columns, terms = zip(*values.items())
        self._columns = [fields[name] for name in columns]
        self._apply_terms(*terms)
        self._replace = False

    @builder
    def update(self):
        if self._update_table is not None or self._selects or self._delete_from:
            raise AttributeError("'Query' object has no attribute '%s'" % "update")

        self._from = []
        self._update_table = self._model

    def join(self, item: t.Any, **kwargs):
        if isclass(item) and issubclass(item, Model):
            item = item.meta.table

        return QueryBuilder.join(self, item, **kwargs)

    async def execute(self: QueryBuilder, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        res = await self._db.execute(sql, *args, **kwargs)
        if self._insert_table:
            params = builder_params(self)
            return self._model(__with_defaults__=False, **dict(params, id=res))

        return res

    def executemany(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not initializated'
        sql = self.get_sql()
        return self._db.executemany(sql, *args, **kwargs)

    def create_table(self: QueryBuilder) -> ModelCreateQueryBuilder:
        meta = self._model.meta
        builder = self.QUERY_CLS.create_table(meta.table, db=self._db, dialect=self.dialect)
        columns = {field.name: Column(
            field.name, column_type=self.DB_TYPES.get(type(field), field.db_type),
            default=field.default if not callable(field.default) else None, nullable=field.null,
        ) for field in meta.fields.values()}

        builder = builder.columns(*columns.values())

        if meta.primary_key:
            builder = builder.primary_key(meta.primary_key)

        for name, field in meta.foreign_keys.items():
            builder = builder.foreign_key(
                [columns[field.name]], field.rel_field.table, [field.rel_field.name])

        return builder

    def drop_table(self: QueryBuilder) -> ModelDropQueryBuilder:
        meta = self._model.meta
        return self.QUERY_CLS.drop_table(meta.table, db=self._db, dialect=self.dialect)


class ModelQuery(Query):

    @classmethod
    def _builder(cls, **kwargs) -> ModelQueryBuilder:
        return ModelQueryBuilder(**kwargs)

    @classmethod
    def create_table(cls, table: t.Union[str, Table], **kwargs) -> ModelCreateQueryBuilder:
        return ModelCreateQueryBuilder(**kwargs).create_table(table)

    @classmethod
    def drop_table(cls, table: t.Union[str, Table], **kwargs) -> ModelDropQueryBuilder:
        return ModelDropQueryBuilder(**kwargs).drop_table(table)


class ModelQueryBuilder(ModelBuilderMixin, QueryBuilder):

    QUERY_CLS = ModelQuery


class ModelCreateQueryBuilder(ModelDBMixin, CreateQueryBuilder):

    QUERY_CLS = ModelQuery


class ModelDropQueryBuilder(ModelDBMixin, DropQueryBuilder):

    QUERY_CLS = ModelQuery


def builder_params(builder: QueryBuilder) -> t.Dict[str, t.Any]:
    if builder._insert_table:
        columns = [term.name for term in builder._columns]
        values = [term.value for row in builder._values for term in row]
        return dict(zip(columns, values))

    return {}


from .model import Model  # noqa
