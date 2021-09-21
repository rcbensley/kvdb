import json
import mariadb
from warnings import filterwarnings


class db:
    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        database: str = "kvdb",
        drop: bool = False,
    ):
        self.table = collection
        self.host = host
        self.database = database
        self.drop = drop
        self.name = f"{self.database}.{self.table}"
        self._db_opts = {
            "host": self.host,
            "autocommit": True,
            "default_file": "~/.my.cnf",
            "default_group": "client",
        }
        self._setup()

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def _setup(self):
        """Create the table to store keys and values."""
        drop_table = f"DROP TABLE IF EXISTS {self.name};"
        create_db = f"CREATE DATABASE IF NOT EXISTS {self.database};"
        create_table = (
            f"CREATE TABLE IF NOT EXISTS {self.name} ("
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
            ") ENGINE=InnoDB WITH SYSTEM VERSIONING;"
        )

        self._cmd(create_db)
        if self.drop:
            self._cmd(drop_table)
        # filterwarnings("error", category=mariadb.Warning)
        self._cmd(create_table)

    def __call__(self):
        self._setup()

    def _query(self, sql: str) -> dict:

        """Query the database."""
        con = mariadb.connect(**self._db_opts)
        cur = con.cursor(dictionary=True, buffered=False)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        con.close()
        return rows

    def _cmd(self, sql: str):
        """Send and SQL command to the database."""
        con = mariadb.connect(**self._db_opts)
        cur = con.cursor(dictionary=True, buffered=False)
        cur.execute(sql)

    def dict2json(self, v: dict):
        """Convert a Python dictionary to JSON"""
        return json.dumps(v)

    def str2json(self, v: str):
        """Convert String to JSON"""
        f_v = v.replace("'", '"')
        f_j = json.loads(f_v)
        return f_j

    def date2str(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

    def get(self, k: str = None, when: str = None):
        """Read key back into JSON dict"""
        d = {
            "table": self.name,
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
            s = "SELECT {cols} FROM {table} {when} {where} {group_by}"
            return s.format(**d)

        def run():
            rows = list()
            rows.extend(self._query(sql=sql()))
            if rows:
                for row in rows:
                    if "v" in row:
                        row["v"] = self.str2json(row["v"])
                    if "created" in row:
                        row["created"] = self.date2str(row["created"])
                    if "updated" in row:
                        row["updated"] = self.date2str(row["updated"])

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
                set_when(f"FOR SYSTEM_TIME AS OF '{when}'")

            if k is not None:
                d["k"] = k
                d["where"] = "WHERE k='{k}'".format(**d)

            if k is None and when in ("first", "last"):
                set_group_by("k")

        init()
        return run()

    def put(self, k: str, v: dict):
        """Insert or Update a key and it's values in the database."""
        row = {"k": k, "v": self.dict2json(v), "kv": ""}
        val_paths = list()
        for i in v.keys():
            val_paths.append("'$.{}', '{}'".format(i, json.dumps(v[i])))

        row["kv"] = ", ".join(val_paths)

        sql = (
            f"INSERT INTO {self.name}" + " (k, v) VALUES  ('{k}', '{v}') "
            "ON DUPLICATE KEY UPDATE v=JSON_SET(v, {kv})"
        ).format(**row)
        self._cmd(sql)

    def update(self, k: str, v: dict):
        """Update a key and it's values in Python, by reading the JSON value
        back into Python, then writing it back to the database."""
        old_row = self.get(k)
        merged_values = dict()
        merged_values.update(old_row["v"])
        merged_values.update(v)
        if old_row:
            self.put(k, merged_values)
        else:
            return False

    def delete(self, k: str):
        """Delete a key."""
        sql = f"DELETE FROM {self.name} WHERE k='{k}'"
        self._cmd(sql)

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
        self.put(k=last["k"], v=last["v"])
