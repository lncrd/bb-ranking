import sqlite3
from typing import Any, List, Optional, Tuple

from utils import SQLITE_DB_PATH


def get_cursor_and_connection() -> Tuple[sqlite3.Cursor, sqlite3.Connection]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return cur, con


def fetch_one_query_result(sql_statement: str, params: Tuple[Any] = (), cur: Optional[sqlite3.Cursor] = None) -> Tuple:
    if cur is None:
        cur, _ = get_cursor_and_connection()
    cur.execute(sql_statement, params)
    return cur.fetchone()


def get_select_query_result(sql_statement: str, params: Tuple[Any] = (), cur: Optional[sqlite3.Cursor] = None) -> List[Tuple]:
    if cur is None:
        cur, _ = get_cursor_and_connection()
    cur.execute(sql_statement, params)
    return cur.fetchall()


def run_param_query(sql_statement: str, params: Tuple = (), cur: Optional[sqlite3.Cursor] = None) -> None:
    if cur is None:
        cur, _ = get_cursor_and_connection()
    cur.execute(sql_statement, params)


def run_many_param_query(sql_statement: str, params: List[Tuple] = (), cur: Optional[sqlite3.Cursor] = None) -> None:
    if cur is None:
        cur, _ = get_cursor_and_connection()
    cur.executemany(sql_statement, params)
