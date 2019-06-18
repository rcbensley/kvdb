from pprint import pprint as pp

from kvdb import Kvdb

db = Kvdb()
db.setup()

db.set('red', {'rgb': [255, 0, 0]})
db.set('blue', {'rgb': [0, 0, 255]})
db.set('green', {'rgb': [0, 255, 0]})

pp(db.get())

