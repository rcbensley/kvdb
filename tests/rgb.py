from time import sleep
from pprint import pprint as pp

import kvdb

db = kvdb.db(history=True)
db.setup()

db.set('red', {'rgb': [254, 0, 0]})
sleep(1)
db.set('blue', {'rgb': [0, 0, 255]})
sleep(1)
db.set('green', {'rgb': [0, 255, 0]})
sleep(1)
pp(db.get())

sleep(5)
#  Oops! Not quite red enough.
db.set('red', {'rgb': [255, 0, 0]})
print('Updated')
pp(db.get('red'))

print('All red:')
pp(db.get_all('red'))

print('Then red:')
pp(db.get_first('red'))

print('All things for all keys:')
pp(db.get(when='all'))

