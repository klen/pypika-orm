import datetime as dt


def test_base():
    from pypika_orm import Model, fields

    class User(Model):
        id = fields.Auto()
        name = fields.Varchar()
        is_active = fields.Bool(default=True)

    assert User
    assert User.meta
    assert User.meta.fields

    assert User.id
    assert isinstance(User.id, fields.Field)

    user = User(name='test', custom_attr='value')
    assert user.name == 'test'
    assert user.is_active is True
    assert user.custom_attr == 'value'


def test_models_equals(User, Role):
    user1 = User(id=1)
    user2 = User(id=2)
    user3 = User(id=1)
    role1 = Role(id=1)

    assert user1 != 42
    assert user1 != role1
    assert user1 != user2
    assert user1 == user3


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
    assert User.meta.primary_key == 'id'

    user = User(name='test', role_id=1, custom='value')
    assert user
    assert user.is_active is True
    assert user.name == 'test'
    assert user.role_id == 1
    assert user.custom == 'value'
    assert isinstance(user.created, dt.datetime)


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

    created = Test.meta.fields['created']
    assert str(created.table) == '"test"'
