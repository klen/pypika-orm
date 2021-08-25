import pytest


@pytest.fixture
def manager():
    from pypika_orm import Manager

    return Manager()


def test_fields(Role, User):
    field = Role.meta.fields['id']
    assert field.db_type == 'INTEGER'
    assert field.py_type == int
    assert field.name == 'id'
    assert field.table

    assert Role.meta.fields['name'].db_type == 'VARCHAR(100)'
    assert Role.meta.fields['name'].default == 'user'

    assert User.meta.fields['name'].db_type == 'VARCHAR(256)'
    assert User.meta.fields['is_active'].default is True

    fk = User.meta.fields['role_id']
    assert fk.db_type == 'INTEGER'
    assert User.meta.foreign_keys == {fk.name: fk}


def test_manager(manager, User):
    assert manager
    assert manager.db is None
    assert manager.dialect is None

    query = manager(User)
    assert query
    assert str(query.select()) == 'SELECT "id","name","created","is_active","role_id" FROM "user"'


def test_select(manager, User, Role):
    qb = manager(User)

    qs = qb.select()
    assert qs
    assert str(qs) == 'SELECT "id","name","created","is_active","role_id" FROM "user"'

    qs = qb.select(User, Role.name).join(Role).on(User.role_id == Role.id).where(User.is_active)
    assert qs
    assert str(qs) == (
        'SELECT "user"."id","user"."name","user"."created",'
        '"user"."is_active","user"."role_id","role"."name" '
        'FROM "user" JOIN "role" ON "user"."role_id"="role"."id" WHERE "user"."is_active"'
    )


def test_insert(manager, User):
    qb = manager(User)

    qs = qb.insert(1, 'test', True)
    assert qs
    assert str(qs) == 'INSERT INTO "user" VALUES (1,\'test\',true)'

    qs = qb.insert(name='test', is_active=False, unknown='ignore')
    assert str(qs) == 'INSERT INTO "user" ("name","is_active") VALUES (\'test\',false)'


def test_update(manager, User):
    qb = manager(User)

    qs = qb.update().set(User.name, 'test2')
    assert qs
    assert str(qs) == 'UPDATE "user" SET "name"=\'test2\''


def test_delete(manager, User):
    qb = manager(User)

    qs = qb.delete()
    assert qs
    assert str(qs) == 'DELETE FROM "user"'


def test_schema(manager, User):
    qb = manager(User)

    qs = qb.create_table().if_not_exists()
    assert qs.get_sql() == (
        'CREATE TABLE IF NOT EXISTS "user" ('
        '"id" INTEGER,'
        '"name" VARCHAR(256),'
        '"created" DATETIME,'
        '"is_active" SMALLINT NOT NULL DEFAULT true,'
        '"role_id" INTEGER,'
        'PRIMARY KEY ("id"),'
        'FOREIGN KEY ("role_id") REFERENCES "role" ("id")'
        ')'
    )

    qs = qb.drop_table().if_exists()
    assert qs.get_sql() == 'DROP TABLE IF EXISTS "user"'
