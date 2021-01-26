import os
from contextlib import closing


def query(db_engine, q):
    rows = None
    with closing(db_engine.raw_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute(q).fetchall()
    return rows


def insert(db_engine, q):
    rows = 0
    with closing(db_engine.raw_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(q)
            connection.commit()
            rows = cursor.lastrowid
    return rows
