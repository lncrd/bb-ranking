import os

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

import ranking
from db_query import get_select_query_result, run_insert_query

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
app.secret_key = os.urandom(12).hex()


@app.route("/")
@app.route("/index")
def index():
    player_solo_elo_list = get_select_query_result(
        """
        SELECT p.name as name, s.mu as solo_elo
        FROM players p
        JOIN solo_ranking s
        ON s.player_id = p.id
        ORDER BY solo_elo DESC
        LIMIT 10
        """
    )

    player_team_elo_list = get_select_query_result(
        """
        SELECT p.name as name, t.mu as team_elo
        FROM players p
        JOIN team_ranking t
        ON t.player_id = p.id
        ORDER BY team_elo DESC
        LIMIT 10
        """
    )

    player_list = get_select_query_result(
        """
        SELECT name
        FROM players
        ORDER BY name ASC
        """
    )

    return render_template(
        "index.html",
        player_solo_elo_list=player_solo_elo_list,
        player_team_elo_list=player_team_elo_list,
        player_list=player_list
    )


@app.route("/add_player", methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        run_insert_query("INSERT INTO players(name) VALUES (?)", (name,))
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

    if not _validate_solo_game_parameters(blue, red, blue_score, red_score):
        return redirect(request.url)

    winner = blue if blue_score > red_score else red
    loser = blue if winner == red else red

    ranking.update_solo_ranking(winner, loser)

    run_insert_query(
        """INSERT INTO solo_game(blue, red, blue_score, red_score, went_under) VALUES (?,?,?,?,?)""",
        (blue, red, blue_score, red_score, went_under)
    )
    flash('Game Added', 'success')
    return redirect(url_for("index"))


def _validate_solo_game_parameters(blue, red, blue_score, red_score):
    """
    Return True if game is valid
    """
    if blue == red:
        flash("You can't play against yourself, dumbass")
        return False
    if blue_score == red_score:
        flash("Ties are not allowed, keep playing")
        return False
    return True


@app.route("/register_team_game", methods=['GET', 'POST'])
def register_team_game():
    if request.method == 'POST':
        print(f"GOT {request.form}")
        return add_team_game_result(request)

    player_list = get_select_query_result("SELECT id, name FROM players")
    return render_template("register_team_game.html", player_list=player_list)


def add_team_game_result(request):
    blue_player1 = int(request.form['blue_player1'])
    blue_player2 = int(request.form['blue_player2'])
    red_player1 = int(request.form['red_player1'])
    red_player2 = int(request.form['red_player2'])
    blue_score = int(request.form['blue_score'])
    red_score = int(request.form['red_score'])
    went_under = "went_under" in request.form and request.form['went_under'] == "on"

    _validate_team_game_parameters(
        blue_player1,
        blue_player2,
        red_player1,
        red_player2,
        blue_score,
        red_score,
    )

    winner = blue if blue_score > red_score else red
    loser = blue if winner == red else red

    ranking.update_solo_ranking(winner, loser)

    run_insert_query(
        """INSERT INTO solo_game(player1, player2, player1_score, player2_score, went_under) VALUES (?,?,?,?,?)""",
        (blue, red, blue_score, red_score, went_under)
    )
    flash('Game Added', 'success')
    return redirect(url_for("index"))


def _validate_team_game_parameters(
    blue_player1: int,
    blue_player2: int,
    red_player1: int,
    red_player2: int,
    blue_score: int,
    red_score: int,
):
    assert blue_player1 != blue_player2 != red_player1 != red_player2, "Players need to be distinct"
    assert blue_score != red_score, "Ties are not allowed"


if __name__ == '__main__':
    app.run(debug=True)
