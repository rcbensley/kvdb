from kvdb import Kvdb
from time import sleep

db = Kvdb()
db.setup()

db.set('a', {'iz_cool': False})
sleep(2)
db.set('a', {'iz_cool': True})
