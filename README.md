Psst, hey, kid, got some dictionaries?

Wanna store those dictionaries?

Check it out, a Key Value Database, or kvdb, in Python.

We can:
* Store dictionaries.
* Retrieve dictionaries.
* Update dictionaries.
* Delete dictionaries (New for version 2).


### Example

Import and setup.
```
import kvdb

db = kvdb.db()
db.setup()
```

Make and store a dictionary.
```
ice_king_stats = {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': True}
db.set('ice_king', ice_king_stats)
```

Wicked. Now let's read if back!
```
print(db.get('ice_king'))
[{'_key': 'ice_king', '_value': {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': True}}]
>>> fixed_stats = {'iz_cool': False}
```

Something is not quite right. Let's fix that key with the correct values.
```
fixed_stats = {'iz_cool': False}
db.update('ice_king', fixed_stats)

print(db.get('ice_king'))
[{'_key': 'ice_king', '_value': {'name': 'Ice King', 'class': 'Wizard', 'iz_cool': False}}]
```
Fixed!

What if we don't want to do any of that messy updating? Simon says, Wizards Rule!

```
cool_stats = {'Wizards': 'Rule'}
db.set('ice_king', cool_stats)
print(db.get('ice_king'))
[{'_key': 'ice_king', '_value': {'Wizards': 'Rule'}}]
```

### NEW In v2!

Let's just forget the whole thing.
```
db.delete('ice_king')
```

### EVEN NEWER in V3!
Blasts from the past.
```
db.get(k='key_name', when='all')
```
The 'when' parameter takes a datetime value, with microsecond precision.

Don't know what you are looking for? Get all versions or just the first version of a key:
```
db.get_first_version(k)
db.get_versoins(k)
```


## Changelog

### v1
Set keys. Get keys. Update keys. Key creation and updating is all still handled within the Python process.

### v2
Delete keys! Can you believe it? Removed type checks, added type notation to the functions parameters.

### v3
Versions.
