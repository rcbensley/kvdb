import json
import pymysql


class db:
    def __init__(self,
                 database='test',
                 history=False):
        self.history = history
        self._db_opts = {'host': '127.0.0.1',
                         'database': database,
                         'autocommit': True,
                         'read_default_file': '~/.my.cnf',
                         'cursorclass': pymysql.cursors.DictCursor}

    def setup(self):
        drop = "DROP TABLE IF EXISTS kvdb"
        create = (
            "CREATE TABLE kvdb ("
            "id bigint(20) NOT NULL AUTO_INCREMENT,"
            "_key varchar(128) NOT NULL,"
            "_value JSON NOT NULL CHECK (JSON_VALID(_value)),"
            "created timestamp(6) NOT NULL "
            "DEFAULT CURRENT_TIMESTAMP() ,"
            "updated timestamp(6) NOT NULL "
            "DEFAULT CURRENT_TIMESTAMP() "
            "ON UPDATE CURRENT_TIMESTAMP(),"
            "PRIMARY KEY (id),"
            "UNIQUE KEY (_key),"
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

    def get(self, k: dict = None, when: str = None):
        if when == 'all':
            h = "FOR SYSTEM_TIME all"
        elif when is not None:
            h = "FOR SYSTEM_TIME AS OF '{}'".format(when)
        else:
            h = ""

        if k is None:
            sql = "SELECT _key,_value FROM kvdb {h}".format(h=h)
        else:
            sql = ("SELECT _key,_value FROM kvdb {h} "
                   " WHERE _key='{k}'").format(k=k, h=h)

        rows = self._query(sql)
        if rows:
            for row in rows:
                if '_value' in row:
                    row['_value'] = self.str2json(row['_value'])

        return rows

    def set(self, k: str, v: dict):
        v = self.dict2json(v)
        sql = ("INSERT INTO kvdb (_key, _value) VALUES  ('{k}', '{v}') "
               "ON DUPLICATE KEY UPDATE _value='{v}'").format(k=k, v=v)
        self._query(sql)

    def update(self, k: str, v: dict):
        old_row = self.get(k)
        if old_row:
            value = old_row[0]['_value']
            value.update(v)
            self.set(k, value)
        else:
            return False

    def delete(self, k: str):
        sql = "DELETE FROM kvdb WHERE _key='{}'".format(k)
        self._query(sql)

    def created_date(self, k: str):
        s = "select created from kvdb where _key='{}'".format(k)
        return self._query(s)

    def get_first_version(self, k: str):
        v = self.created_date(k)
        date = v[0]['created']
        if v is not False:
            return(self.get(k=k, when=date))

    def get_versions(self, k: str):
        return self.get(k=k, when='all')

