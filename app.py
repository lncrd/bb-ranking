from typing import List, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

from utils import SQLITE_DB_PATH

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT name, solo_elo FROM players ORDER BY solo_elo DESC")
    data = cur.fetchall()
    return render_template("index.html", datas=data)


@app.route("/players")
def players() -> List[str]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name FROM players ORDER BY name")
    return cur.fetchall()


@app.route("/add_player", methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        print(f"GOT {request.form}")
        name = request.form['name']
        con = sqlite3.connect(SQLITE_DB_PATH)
        cur = con.cursor()
        cur.execute("INSERT INTO players(name) VALUES (?)", (name,))
        con.commit()
        flash('User Added', 'success')
        return redirect(url_for("index"))
    return render_template("add_player.html")


@app.route("/register_solo_game", methods=['POST'])
def add_game_result():
    player1 = request.form['player1']
    player2 = request.form['player2']
    player1_score = request.form['player1_score']
    player2_score = request.form['player2_score']
    went_under = request.form['went_under']

    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute(
        """"
        INSERT INTO solo_game(
            player1
            player2
            player1_score
            player2_score
            went_under
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            player1,
            player2,
            player1_score,
            player2_score,
            went_under,
        )
    )
    con.commit()


if __name__ == '__main__':
    app.secret_key = 'foobar1234'
    app.run(debug=True)
