from __future__ import annotations

import typing as t

from pypika.queries import Table
from pypika.dialects import (
    Dialects, PostgreSQLQueryBuilder,
    MySQLQuery, MySQLQueryBuilder, SQLLiteQueryBuilder
)

from . import fields
from .query import ModelBuilderMixin, ModelQuery, ModelCreateQueryBuilder, ModelDropQueryBuilder


DIALECT_TO_BUILDER = {}


# Postgres
# --------

class ModelPostgreSQLQuery(ModelQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelPostgreSQLQueryBuilder(**kwargs)


class ModelPostgreSQLQueryBuilder(ModelBuilderMixin, PostgreSQLQueryBuilder):

    QUERY_CLS = ModelPostgreSQLQuery
    DB_TYPES = {
        fields.Auto: 'SERIAL',
        fields.BigAuto: 'BIGSERIAL',
        fields.Blob: 'BYTEA',
        fields.Bool: 'BOOLEAN',
        fields.Datetime: 'TIMESTAMP',
        fields.Decimal: 'NUMERIC',
        fields.Double: 'DOUBLE PRECISION',
        fields.UUID: 'UUID',
        fields.UUIDB: 'BYTEA',
    }


DIALECT_TO_BUILDER[Dialects.POSTGRESQL] = ModelPostgreSQLQueryBuilder


# MySQL
# -----


class ModelMySQLQuery(MySQLQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelMySQLQueryBuilder(**kwargs)

    @classmethod
    def create_table(cls, table: t.Union[str, Table], **kwargs) -> ModelCreateQueryBuilder:
        return ModelMySQLCreateQueryBuilder(**kwargs).create_table(table)

    @classmethod
    def drop_table(cls, table: t.Union[str, Table], **kwargs) -> ModelCreateQueryBuilder:
        return ModelMySQLDropQueryBuilder(**kwargs).drop_table(table)


class ModelMySQLQueryBuilder(ModelBuilderMixin, MySQLQueryBuilder):

    QUERY_CLS = ModelMySQLQuery
    DB_TYPES = {
        fields.Auto: 'INTEGER AUTO_INCREMENT',
        fields.BigAuto: 'BIGINT AUTO_INCREMENT',
        fields.Bool: 'BOOL',
        fields.Decimal: 'NUMERIC',
        fields.Double: 'DOUBLE PRECISION',
        fields.Float: 'FLOAT',
        fields.UUID: 'VARCHAR(40)',
        fields.UUIDB: 'VARBINARY(16)',
    }


class ModelMySQLCreateQueryBuilder(ModelCreateQueryBuilder):

    QUOTE_CHAR = MySQLQueryBuilder.QUOTE_CHAR


class ModelMySQLDropQueryBuilder(ModelDropQueryBuilder):

    QUOTE_CHAR = MySQLQueryBuilder.QUOTE_CHAR


DIALECT_TO_BUILDER[Dialects.MYSQL] = ModelMySQLQueryBuilder


# SQLite
# ------

class ModelSQLLiteQuery(ModelQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelSQLLiteQueryBuilder(**kwargs)


class ModelSQLLiteQueryBuilder(ModelBuilderMixin, SQLLiteQueryBuilder):

    QUERY_CLS = ModelSQLLiteQuery


DIALECT_TO_BUILDER[Dialects.SQLLITE] = ModelSQLLiteQueryBuilder
