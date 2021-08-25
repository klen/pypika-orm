import pytest


@pytest.fixture(scope='module')
async def db_url():
    return 'sqlite:///:memory:'


@pytest.fixture(scope='module', autouse=True)
async def setup(manager, Role, User):
    await manager(Role).create_table().if_not_exists().execute()
    await manager(User).create_table().if_not_exists().execute()
    yield
    await manager(User).drop_table().if_exists().execute()
    await manager(Role).drop_table().if_exists().execute()


async def test_builder(User, manager):
    assert repr(manager) == '<Manager sqlite:///:memory:>'

    from pypika_orm.dialects import ModelSQLLiteQueryBuilder

    UserManager = manager(User)
    assert type(UserManager) is ModelSQLLiteQueryBuilder


async def test_db(manager, User, Role):
    res = await manager(Role).insert(name='user').execute()
    assert res

    res = await manager(Role).insert(name='admin').execute()
    assert res

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
