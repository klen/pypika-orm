import pytest


@pytest.fixture(scope='module')
def db_url():
    return 'sqlite:///:memory:'


@pytest.fixture(scope='module')
async def manager(db_url):
    from pypika_orm import Manager

    async with Manager(db_url) as manager:
        yield manager


@pytest.fixture(scope='session')
def Role():
    from pypika_orm import Model, fields

    class Role(Model):
        id = fields.Auto()
        name = fields.Varchar(max_length=100, default='user')

    return Role


@pytest.fixture(scope='session')
def User(Role):
    from pypika_orm import Model, fields

    class User(Model):
        id = fields.Auto()
        name = fields.Varchar()
        is_active = fields.Bool(default=True, null=False)

        role_id = fields.ForeignKey(Role.id)

    return User
