import pytest


@pytest.fixture(scope='module')
async def db_url():
    return 'postgresql://test:test@localhost:5432/tests'


@pytest.fixture(scope='module', autouse=True)
async def setup(manager, Role, User):
    await manager(Role).create_table().if_not_exists()
    await manager(User).create_table().if_not_exists()
    yield
    await manager(User).drop_table().if_exists()
    await manager(Role).drop_table().if_exists()


async def test_builder(User, manager):
    assert repr(manager) == '<Manager postgresql://test:test@localhost:5432/tests>'

    from pypika_orm.dialects import ModelPostgreSQLQueryBuilder

    UserManager = manager(User)
    assert type(UserManager) is ModelPostgreSQLQueryBuilder


async def test_create_table(User, manager):
    assert str(manager(User).create_table()) == (
        'CREATE TABLE "user" ('
        '"id" SERIAL,'
        '"name" VARCHAR(256),'
        '"created" TIMESTAMP,'
        '"is_active" BOOLEAN NOT NULL DEFAULT true,'
        '"role_id" INTEGER,'
        'PRIMARY KEY ("id"),'
        'FOREIGN KEY ("role_id") REFERENCES "role" ("id")'
        ')'
    )


async def test_drop_table(manager, User):
    UserManager = manager(User)

    assert UserManager.drop_table().get_sql() == 'DROP TABLE "user"'


async def test_db(manager, User, Role):
    await manager(Role).insert(name='user')
    await manager(Role).insert(name='admin')

    [role1, role2] = await manager(Role).select().fetchall()
    assert isinstance(role1, Role)
    assert role1.id == 1
    assert role1.name == 'user'
    assert role2.id == 2
    assert role2.name == 'admin'

    role = await manager(Role).select().fetchone()
    assert isinstance(role, Role)
    assert role.id == 1
    assert role.name == 'user'

    await manager(User).insert(name='jim', role_id=1)
    [user] = await manager(User).select().fetchall()
    assert user.id == 1
    assert user.name == 'jim'
    assert user.role_id == 1

    qs = manager(User).select(User, Role).join(Role).on(
        User.role_id == Role.id).where(User.is_active)

    [rec] = await manager.fetchall(qs)
    assert rec
