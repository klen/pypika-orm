import pytest


@pytest.fixture(scope='module')
async def db_url():
    return 'mysql://root@127.0.0.1:3306/tests'


@pytest.fixture(scope='module', autouse=True)
async def setup(manager, Role, User):
    await manager(Role).create_table().if_not_exists().execute()
    await manager(User).create_table().if_not_exists().execute()
    yield
    await manager(User).drop_table().if_exists().execute()
    await manager(Role).drop_table().if_exists().execute()


async def test_builder(User, manager):
    assert repr(manager) == '<Manager mysql://root@127.0.0.1:3306/tests>'

    from pypika_orm.dialects import ModelMySQLQueryBuilder

    UserManager = manager(User)
    assert type(UserManager) is ModelMySQLQueryBuilder


async def test_create_table(User, manager):
    assert str(manager(User).create_table()) == (
        'CREATE TABLE `user` ('
        '`id` INTEGER AUTO_INCREMENT,'
        '`name` VARCHAR(256),'
        '`created` DATETIME,'
        '`is_active` BOOL NOT NULL DEFAULT true,'
        '`role_id` INTEGER,'
        'PRIMARY KEY (`id`),'
        'FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)'
        ')'
    )


async def test_drop_table(manager, User):
    UserManager = manager(User)

    assert UserManager.drop_table().get_sql() == "DROP TABLE `user`"


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
