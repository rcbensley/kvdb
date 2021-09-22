import kvdb

db = kvdb.db("colours", drop=True)

db.set("red", {"rgb": [255, 0, 0]})
db.set("green", {"rgb": [0, 255, 0]})
db.set("blue", {"rgb": [0, 0, 255]})
db.get()

db.set(
    "red",
    {
        "things": [
            "Tractor",
        ]
    },
)
db.get("red")


db.set(
    "red",
    {
        "things": [
            "Fire Engine",
        ]
    },
)
db.get("red")

db.update(
    "red",
    {
        "things": ["Tractor"],
    },
)
db.get("red")

db.get("red", when="all")


# Restore
what = "red"
when = db.get_first("red")["created"]
print(when)
all = db.get_first("red")
print(all)

db.restore(k=what, when=when)
