from kvdb import Kvdb
from datetime import datetime as dt
from datetime import timedelta as td

db = Kvdb()
db.setup()


weekly_watch_list = [
    {"title": "Blade Runner", "Director": "Ridley Scott"},
    {"title": "Frozen", "Director": ["Chris Buck", "Jennifer Lee"]},
    {"title": "Jumanji", "Director": "Joe Johnston"},
    {"title": "Labyrinth", "Director": "Jim Henson"},
    {"title": "Pixels", "Director": "Chris Columbus"},
    {"title": "Jack and Jill", "Director": "Dennis Dugan"},
    {"title": "Transformers: The Last knight", "Director": "Michael Bay"}
]

week_start = dt(year=2019, month=6, day=10)
week = [week_start + td(days=i) for i in range(0, len(weekly_watch_list))]


def gotta_watch_em_all(films):
    for i in range(0, len(films)):
        date = week_start + td(days=i)
        date_key = dt.strftime(date, '%Y-%m-%d')
        film = weekly_watch_list[i]
        db.set(k=date_key, v=film)

        question = f"Is {film['title']}, currently your favourite film? (y or n)"
        answer = input(question)
        if answer == 'y':
            db.set(k='favourite', v={**film, **{"date": date_key}})


gotta_watch_em_all(weekly_watch_list)

