import sqlite3
from typing import Any, List, Tuple

from utils import SQLITE_DB_PATH


def fetch_one_query_result(sql_statement: str, params: Tuple[Any] = ()) -> Tuple:
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql_statement, params)
    return cur.fetchone()


def get_select_query_result(sql_statement: str, params: Tuple[Any] = ()) -> List[Tuple]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql_statement, params)
    return cur.fetchall()


def run_insert_query(sql_statement: str, params: Tuple = ()) -> None:
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql_statement, params)
    con.commit()
