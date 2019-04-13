Key-Value-Database
-----------------
kvdb is a toy abstraction layer allowing one to persist Python dictionaries to a real database.

kvdb is supposed to be simple, similar to Shelve, PickleDB, etc.

A new database is setup simply with:
```
import kvdb
db = kvdb.db()
db.setup()
```

Store a dictionary:
```
ice_king_stats = {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': True}
db.set('ice_king', ice_king_stats)
```

Retrieve a dictionary:
```
print(db.get('ice_king'))
[{'_key': 'ice_king', '_value': {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': True}}]
```

Update the dictionary:
```
fixed_stats = {'iz_cool': False}
db.update('ice_king', fixed_stats)
print(db.get('ice_king'))
[{'_key': 'ice_king', '_value': {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': False}}]
```

In the background the data is being written to a MariaDB table. The dictionary is converted to JSON and inserted into a JSON data type column.
By default, system versioniong is enabled, so all key revisions are stored and retrievable down to the millisecond.

```
db.get(k='ice_king', when='all')
[{'k': 'ice_king',
  'v': {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': True},
  'created': datetime.datetime(2019, 4, 13, 10, 58, 7, 410291),
  'updated': datetime.datetime(2019, 4, 13, 10, 58, 7, 410291)},
 {'k': 'ice_king',
  'v': {'name': '"Ice King"', 'class': '"Wizard"', 'iz_cool': 'true'},
  'created': datetime.datetime(2019, 4, 13, 10, 58, 7, 410291),
  'updated': datetime.datetime(2019, 4, 13, 10, 58, 22, 272612)}]
```
