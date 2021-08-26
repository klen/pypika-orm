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


@pytest.fixture(autouse=True)
async def transaction(manager):
    """Run every test and rollback the transaction to reset database."""
    async with manager.transaction() as trans:
        yield
        await trans.rollback()


async def test_builder(User, manager):
    assert repr(manager) == '<Manager sqlite:///:memory:>'

    from pypika_orm.dialects import ModelSQLLiteQueryBuilder

    UserManager = manager(User)
    assert type(UserManager) is ModelSQLLiteQueryBuilder


async def test_insert(manager, User, Role):
    role = await manager(Role).insert(name='user').execute()
    assert role
    assert isinstance(role, Role)
    assert role.id == 1
    assert role.name == 'user'
    assert role.created is None

    user = await manager(User).insert(name='jim', role_id=role.id).execute()
    assert user
    assert isinstance(user, User)
    assert user.id == 1
    assert user.name == 'jim'


async def test_save(manager, Role):
    role = Role(name='user')
    role = await manager.save(role)
    assert role
    assert role.id == 1
    assert role.name == 'user'

    role2 = await manager(Role).select().fetchone()
    assert role == role2

    #  role.name = 'guest'
    #  role = await manager.save(role)


async def test_db(manager, User, Role):
    role = await manager(Role).insert(name='user').execute()
    assert role
    assert role.id

    role = await manager(Role).insert(name='admin').execute()
    assert role
    assert role.id

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

    await manager(User).insert(name='jim', role_id=role1.id).execute()
    [user] = await manager(User).select().fetchall()
    assert user.id == 1
    assert user.name == 'jim'
    assert user.role_id == 1

    qs = manager(User).select(User, Role).join(Role).on(
        User.role_id == Role.id).where(User.is_active)

    [rec] = await manager.fetchall(qs)
    assert rec
    assert list(rec) == [1, 'jim', None, 1, 1, 1, 'user', None]
