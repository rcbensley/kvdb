import json
import pymysql


class db:
    def __init__(self,
                 database='test',
                 history=False):
        self.database = database
        self.history = history
        self._db_opts = {'host': '127.0.0.1',
                         'database': database,
                         'autocommit': True,
                         'read_default_file': '~/.my.cnf',
                         'cursorclass': pymysql.cursors.DictCursor}

    def __repr__(self):
        return self.get()

    def setup(self):
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
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")

        add_history = "ALTER TABLE kvdb ADD SYSTEM VERSIONING;"

        self._query(drop)
        self._query(create)
        if self.history is True:
            self._query(add_history)

    def _query(self, sql: str):
        con = pymysql.connect(**self._db_opts)
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        con.close()
        if rows:
            return rows
        else:
            return False

    def dict2json(self, v: dict):
        return(json.dumps(v))

    def str2json(self, v: str):
        f_v = v.replace("'", "\"")
        f_j = json.loads(f_v)
        return f_j

    def get(self, k: str = None, when: str = None):
        d = {
            'cols': 'k, v',
            'db': self.database,
            'when': '',
            'where': '',
            'group_by': ''
        }

        def add_cols(i: str):
            d['cols'] = d['cols'] + i

        def set_when(i: str):
            d['when'] = i

        def set_group_by(i):
            d['group_by'] = "GROUP BY {}".format(i)

        def sql():
            s = "SELECT {cols} FROM '{db}'.kvdb {when} {where} {group_by}"
            return s.format(**d)

        def run():
            rows = self._query(sql=sql())
            if rows:
                for row in rows:
                    if 'v' in row:
                        row['v'] = self.str2json(row['v'])

            if len(rows) == 1 and type(rows) is list:
                return rows[0]
            elif len(rows) > 1:
                return rows
            else:
                return False

        def init():
            if when == 'all':
                set_when("FOR SYSTEM_TIME all")
            elif when == 'first':
                add_cols(", min(created) as created")
                set_when("FOR SYSTEM_TIME all")
            elif when == 'last':
                add_cols(", max(updated) as updated")
                set_when("FOR SYSTEM_TIME all")
            elif when is not None:
                set_when("FOR SYSTEM_TIME AS OF '{}'".format(when))

            if k is not None:
                d['where'] = "WHERE k='{k}'"

            if k is None and when in ('first', 'last'):
                set_group_by('k')

            if k is not None:
                d['k'] = k

        init()
        run()

    def key_exists(self, k):
        return self.get(k=k)

    def set(self, k: str, v: dict):
        if self.key_exists(k=k) is not False:
            v = self.dict2json(v)
            sql = ("INSERT INTO kvdb (k, v) VALUES  ('{k}', '{v}') "
                   "ON DUPLICATE KEY UPDATE v='{v}'").format(k=k, v=v)
            self._query(sql)
        else:
            self.update(k=k, v=v)

    def update(self, k: str, v: dict):
        old_row = self.get(k)
        if old_row:
            value = old_row[0]['v']
            value.update(v)
            self.set(k, value)
        else:
            return False

    def delete(self, k: str):
        sql = "DELETE FROM kvdb WHERE k='{}'".format(k)
        self._query(sql)

    def get_last(self, k: str = None):
        return self.get(k=k, when='last')

    def get_first(self, k: str = None):
        return self.get(k=k, when='first')

    def get_all(self, k: str = None):
        return self.get(k=k, when='all')

    def restore(self, k: str):
        last = self.get(k=k, when='last')
        db.set(**last)
