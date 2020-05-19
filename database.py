import sqlite3
from multiprocessing import Lock


class Database:
    """
    Multiprocessing-safe access to the runs database.
    """

    def __init__(self):
        self.lock = Lock()
        self.conn = sqlite3.connect("runs.sqlite")
        self.conn.executescript(open("db_schema.sql", "r").read())
        self.conn.commit()

    def _get_identifying_id(self, table: str, col: str, value: str) -> id:
        self.lock.acquire()
        computer = self.conn.execute(f"SELECT id FROM {table} WHERE {col}=?",
                                     value).fetchone()
        if computer is not None:
            self.lock.release()
            return computer[0]

        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO {table} ({col}) VALUES (?)", value)
        computer_id = cur.lastrowid
        cur.close()
        self.conn.commit()

        self.lock.release()

        return computer_id

    def get_computer_id(self, name: str) -> int:
        return self._get_identifying_id("computers", "name", name)

    def get_version_id(self, hex: str) -> int:
        return self._get_identifying_id("versions", "hex", hex)
