from typing import List, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

from utils import SQLITE_DB_PATH

app = Flask(__name__)


@app.route("/leaderboard")
def leaderboard() -> List[Tuple[str, int]]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name, elo FROM players ORDER BY elo DESC")
    return cur.fetchall()


@app.route("/players")
def players() -> List[str]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name FROM players ORDER BY name")
    return cur.fetchall()


@app.route("/add_player", methods=['POST'])
def add_player():
    name = request.form['name']
    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO players(name) VALUES (?)", name)
    con.commit()


def add_game_result():
    # TODO
    pass


if __name__ == '__main__':
    app.secret_key = 'foobar1234'
    app.run(debug=True)
