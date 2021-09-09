# PyPika-ORM - ORM for PyPika SQL Query Builder

The package gives you ORM for [PyPika](https://github.com/kayak/pypika) with
asycio support for a range of databases (SQLite, PostgreSQL, MySQL).

[![Tests Status](https://github.com/klen/pypika-orm/workflows/tests/badge.svg)](https://github.com/klen/pypika-orm/actions)
[![PYPI Version](https://img.shields.io/pypi/v/pypika-orm)](https://pypi.org/project/pypika-orm/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypika-orm)](https://pypi.org/project/pypika-orm/)


## Warning

The project is in early pre-alpha state and not ready for production

## Requirements

* python >= 3.7

## Installation

**pypyka-orm** should be installed using pip:

```shell
$ pip install pypika-orm
```

You can install the required database drivers with:

```shell
$ pip install pypika-orm[sqlite]
$ pip install pypika-orm[postgresql]
$ pip install pypika-orm[mysql]
```

## Usage

```python
    from pypika_orm import Model, fields

    class Role(Model):
        id = fields.Auto()
        name = fields.Varchar(max_length=100, default='user')

    class User(Model):
        id = fields.Auto()
        name = fields.Varchar()
        is_active = fields.Bool(default=True, null=False)

        role_id = fields.ForeignKey(Role.id)

    from pypika_orm import Manager

    async with Manager('sqlite:///:memory:') as manager:
        await manager(Role).create_table().if_not_exists()
        await manager(User).create_table().if_not_exists()

        await manager(Role).insert(name='user')
        await manager(User).insert(name='jim', role_id=1)

        [user] = await manager(User).select().fetchall()
        assert user
```

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at https://github.com/klen/pypika-orm/issues


## Contributing

Development of the project happens at: https://github.com/klen/pypika-orm


## License

Licensed under a [MIT License](http://opensource.org/licenses/MIT)

