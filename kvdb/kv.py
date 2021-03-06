import json
import pymysql
from warnings import filterwarnings


class Kvdb:
    def __init__(self, database="kvdb", history=True):
        self.database = database
        self.history = history
        self._db_opts = {
            "host": "127.0.0.1",
            "database": self.database,
            "autocommit": True,
            "read_default_file": "~/.my.cnf",
            "cursorclass": pymysql.cursors.DictCursor,
        }

    def setup(self):
        """Create the table used by kvdb to store key/values."""
        drop = "DROP TABLE IF EXISTS kvdb"
        create = (
            "CREATE TABLE kvdb ("
            "id bigint(20) NOT NULL AUTO_INCREMENT,"
            "k varchar(128) NOT NULL,"
            "v JSON NOT NULL CHECK (JSON_VALID(v)),"
            "created timestamp(6) NOT NULL "
            "DEFAULT CURRENT_TIMESTAMP() ,"
            "updated timestamp(6) NOT NULL "
            "DEFAULT CURRENT_TIMESTAMP() "
            "ON UPDATE CURRENT_TIMESTAMP(),"
            "PRIMARY KEY (id),"
            "UNIQUE KEY (k),"
            "INDEX idx_date (created, updated)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

        add_history = "ALTER TABLE kvdb ADD SYSTEM VERSIONING;"

        self._query(drop)
        filterwarnings('error', category=pymysql.Warning)
        self._query(create)
        if self.history is True:
            self._query(add_history)

    def _query(self, sql: str):
        """Query the database."""
        con = pymysql.connect(**self._db_opts)
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        con.close()
        return rows

    def dict2json(self, v: dict):
        """Convert a Python dictionary to JSON"""
        return json.dumps(v)

    def str2json(self, v: str):
        """Convert String to JSON"""
        f_v = v.replace("'", '"')
        f_j = json.loads(f_v)
        return f_j

    def date2str(self, dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    def get(self, k: str = None, when: str = None):
        """Read key back into JSON dict"""
        d = {
            "cols": "k, v",
            "db": self.database,
            "when": "",
            "where": "",
            "group_by": "",
        }

        def add_cols(i: str):
            d["cols"] = d["cols"] + i

        def set_when(i: str):
            d["when"] = i

        def set_group_by(i):
            d["group_by"] = "GROUP BY {}".format(i)

        def sql():
            s = "SELECT {cols} FROM `{db}`.kvdb {when} {where} {group_by}"
            return s.format(**d)

        def run():
            rows = list()
            rows.extend(self._query(sql=sql()))
            if rows:
                for row in rows:
                    if 'v' in row:
                        row['v'] = self.str2json(row["v"])
                    if 'created' in row:
                        row['created'] = self.date2str(row['created'])
                    if 'updated' in row:
                        row['updated'] = self.date2str(row['updated'])

            if rows:
                if len(rows) == 1:
                    return rows[0]
                else:
                    return rows
            else:
                return rows

        def init():
            if when == "all":
                add_cols(", created, updated")
                set_when("FOR SYSTEM_TIME all")
            elif when == "first":
                add_cols(", min(created) as created")
                set_when("FOR SYSTEM_TIME all")
            elif when == "last":
                add_cols(", max(updated) as updated")
                set_when("FOR SYSTEM_TIME all")
            elif when is not None:
                set_when("FOR SYSTEM_TIME AS OF '{}'".format(when))

            if k is not None:
                d["k"] = k
                d["where"] = "WHERE k='{k}'".format(**d)

            if k is None and when in ("first", "last"):
                set_group_by("k")

        init()
        return run()

    def set(self, k: str, v: dict):
        """Insert or Update a key and it's values in the database."""
        row = {"k": k, "v": self.dict2json(v), "kv": ""}
        val_paths = list()
        for i in v.keys():
            val_paths.append("'$.{}', '{}'".format(i, json.dumps(v[i])))

        row["kv"] = ", ".join(val_paths)

        sql = (
            "INSERT INTO kvdb (k, v) VALUES  ('{k}', '{v}') "
            "ON DUPLICATE KEY UPDATE v=JSON_SET(v, {kv})"
        ).format(**row)
        self._query(sql)

    def update(self, k: str, v: dict):
        """Update a key and it's values in Python, by reading the JSON value
        back into Python, then writing it back to the database."""
        old_row = self.get(k)
        merged_values = dict()
        merged_values.update(old_row['v'])
        merged_values.update(v)
        if old_row:
            self.set(k, merged_values)
        else:
            return False

    def delete(self, k: str):
        """Delete a key."""
        sql = "DELETE FROM kvdb WHERE k='{}'".format(k)
        self._query(sql)

    def get_last(self, k: str = None):
        """Get the latest version of a key and it's values."""
        return self.get(k=k, when="last")

    def get_first(self, k: str = None):
        """Get the first version of a key and it's values."""
        return self.get(k=k, when="first")

    def get_all(self, k: str = None):
        """Get all versions of all keys or a specified keys."""
        return self.get(k=k, when="all")

    def restore(self, k: str, when):
        """Restore a version of a deleted key."""
        last = self.get(k=k, when=when)
        self.delete(k=k)
        self.set(k=last['k'], v=last['v'])
