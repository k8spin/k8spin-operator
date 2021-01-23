import os
import sqlite3
from contextlib import closing

PATH = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = f"{PATH}/../../k8spin.db"


def query(q):
    rows = None
    with closing(sqlite3.connect(DB_FILE_PATH)) as connection:
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute(q).fetchall()
    return rows


def insert(q):
    rows = 0
    with closing(sqlite3.connect(DB_FILE_PATH)) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(q)
            connection.commit()
            rows = cursor.lastrowid
    return rows
