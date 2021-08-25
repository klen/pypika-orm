import pytest

import datetime as dt


def test_models(User, Role):
    assert Role
    assert Role.meta
    assert Role.meta.fields

    role = Role(name='test')
    assert role
    assert role.name
    assert isinstance(role.created, dt.datetime)

    assert User
    assert User.meta.fields
    assert User.meta.primary_key == ('id',)

    user = User(name='test', role_id=1, custom='value')
    assert user
    assert user.is_active is True
    assert user.name == 'test'
    assert user.role_id == 1
    assert user.custom == 'value'
    assert isinstance(user.created, dt.datetime)


@pytest.mark.skip
def test_inheritance():
    from pypika_orm import Model, fields

    class TimeModel(Model):
        created = fields.Datetime(default=dt.datetime.utcnow)

    class Test(TimeModel):
        id = fields.Auto()
        name = fields.Varchar()

    assert Test
    assert Test.meta
    assert Test.meta.fields
    assert 'created' in Test.meta.fields
