import os
import sqlite3
from typing import List, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

from utils import SQLITE_DB_PATH

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
app.secret_key = os.urandom(12).hex()


def get_select_query_result(sql_statement: str) -> List[Tuple]:
    con = sqlite3.connect(SQLITE_DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql_statement)
    return cur.fetchall()


@app.route("/")
@app.route("/index")
def index():
    player_elo_list = get_select_query_result("SELECT name, solo_elo FROM players ORDER BY solo_elo DESC")
    return render_template("index.html", player_elo_list=player_elo_list)


@app.route("/add_player", methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        con = sqlite3.connect(SQLITE_DB_PATH)
        cur = con.cursor()
        cur.execute("INSERT INTO players(name) VALUES (?)", (name,))
        con.commit()
        flash('User Added', 'success')
        return redirect(url_for("index"))
    return render_template("add_player.html")


@app.route("/register_solo_game", methods=['GET', 'POST'])
def register_solo_game():
    if request.method == 'POST':
        print(f"GOT {request.form}")
        return add_solo_game_result(request)

    player_list = get_select_query_result("SELECT id, name FROM players")
    return render_template("register_solo_game.html", player_list=player_list)


def add_solo_game_result(request):
    blue = int(request.form['blue'])
    red = int(request.form['red'])
    blue_score = int(request.form['blue_score'])
    red_score = int(request.form['red_score'])
    went_under = "went_under" in request.form and request.form['went_under'] == "on"

    _validate_solo_game_parameters(blue, red, blue_score, red_score)

    con = sqlite3.connect(SQLITE_DB_PATH)
    cur = con.cursor()
    cur.execute(
        """INSERT INTO solo_game(player1, player2, player1_score, player2_score, went_under) VALUES (?,?,?,?,?)""",
        (blue, red, blue_score, red_score, went_under)
    )
    con.commit()
    flash('Game Added', 'success')
    return redirect(url_for("index"))


def _validate_solo_game_parameters(blue, red, blue_score, red_score):
    assert blue != red, "You can't play against yourself dumbass"
    assert blue_score != red_score, "Ties are not allowed"


if __name__ == '__main__':
    app.run(debug=True)
