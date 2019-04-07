import kvdb
from pprint import pprint as pp

db = kvdb.db()

db.setup()

db.set('Do Androids Dream of Electric Sheep',
       {'format': 'Paperback',
        'pages': '210',
        'author': 'Phillip K. Dick'})
db.set('Blade Runner',
       {'format': 'DVD',
        'running_time': '117 minutes'})
db.set('Blade Runner 2049',
       {'format': 'Blu-Ray',
        'running_time': '163 minutes',
        'Director': 'Denis Villeneuve'})

pp(db.get('Blade Runner'))

db.set('Blade Runner', {'Director': 'Ridley Scott'})

pp(db.get())
