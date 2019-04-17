import kvdb
from time import sleep

db = kvdb.db()
db.setup()

db.set('a', {'iz_cool': False})
sleep(2)
db.set('a', {'iz_cool': True})
