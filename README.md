# PyPika-ORM - ORM for PyPika SQL Query Builder

The package gives you ORM for [PyPika](https://github.com/kayak/pypika) with
asycio support for a range of databases (SQLite, PostgreSQL, MySQL).

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
    from aio_databases import Database

    db = Database('sqlite:///:memory:')

    await db.execute('select $1', '1')
    await db.executemany('select $1', '1', '2', '3')

    res = await db.fetchall('select (2 * $1) res', 2)
    assert res == [(4,)]

    res = await db.fetchone('select (2 * $1) res', 2)
    assert res == (4,)
    assert isinstance(res, db.backend.record_cls)

    res = await db.fetchval('select 2 * $1', 2)
    assert res == 4

```

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at https://github.com/klen/aio-databases/issues


## Contributing

Development of the project happens at: https://github.com/klen/aio-databases


## License

Licensed under a [MIT License](http://opensource.org/licenses/MIT)

