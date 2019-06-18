from kvdb import Kvdb

db = Kvdb()
db.setup()

db.set('red', {'rgb': [255, 0, 0]})
db.set('blue', {'rgb': [0, 0, 255]})
db.set('green', {'rgb': [0, 255, 0]})
db.get()

db.set('red', {'things': ['Tractor', ]})
db.get('red')


db.set('red', {'things': ['Fire Engine', ]})
db.get('red')

db.update('red', {'things': ['Tractor'], })
db.get('red')

db.get('red', when='all')
