import os

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

import rating
from db_query import get_select_query_result, run_param_query, get_cursor_and_connection, fetch_one_query_result
from model import Player, SoloGame, Team, TeamGame

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
app.secret_key = os.urandom(12).hex()


@app.route("/")
@app.route("/index")
def index():
    cur, _ = get_cursor_and_connection()

    player_solo_elo_list = get_select_query_result(
        """
        SELECT 
            p.name AS name,
            ROUND(sr.mu, 2) AS solo_elo
        FROM players p
        JOIN solo_ranking sr
        ON sr.player_id = p.id
        JOIN (
            SELECT player_id, MAX(game_id) AS max_game_id
            FROM solo_ranking
            GROUP BY player_id
        ) sr2
        ON sr2.player_id = sr.player_id AND sr2.max_game_id = sr.game_id
        ORDER BY solo_elo DESC
        LIMIT 10
        """,
        cur=cur
    )

    player_team_elo_list = get_select_query_result(
        """
        SELECT 
            p.name AS name,
            ROUND(sr.mu, 2) AS team_elo
        FROM players p
        JOIN team_ranking sr
        ON sr.player_id = p.id
        JOIN (
            SELECT player_id, MAX(game_id) AS max_game_id
            FROM team_ranking
            GROUP BY player_id
        ) sr2
        ON sr2.player_id = sr.player_id AND sr2.max_game_id = sr.game_id
        ORDER BY team_elo DESC
        LIMIT 10
        """,
        cur=cur
    )

    return render_template(
        "index.html",
        player_solo_elo_list=player_solo_elo_list,
        player_team_elo_list=player_team_elo_list,
    )


@app.route("/players")
def players():
    cur, _ = get_cursor_and_connection()

    player_list = get_select_query_result(
        """
        SELECT name
        FROM players
        ORDER BY name ASC
        """,
        cur=cur
    )

    return render_template(
        "players.html",
        player_list=player_list,
    )


@app.route("/solo_games")
def solo_games():
    cur, _ = get_cursor_and_connection()

    recent_solo_games = get_select_query_result(
        """
        SELECT p_blue.name as blue_name, p_red.name as red_name, blue_score, red_score, sg.created_timestamp 
        FROM solo_game sg
        JOIN players p_blue
        ON sg.blue = p_blue.id
        JOIN players p_red
        ON sg.red = p_red.id
        ORDER BY sg.created_timestamp DESC
        LIMIT 25
        """,
        cur=cur
    )

    return render_template(
        "solo_games.html",
        recent_solo_games=recent_solo_games,
    )


@app.route("/team_games")
def team_games():
    cur, _ = get_cursor_and_connection()

    recent_team_games = get_select_query_result(
        """
        SELECT 
         p_blue_attacker.name as blue_attacker_name, p_blue_defender.name as blue_defender_name,
         p_red_attacker.name as red_attacker_name, p_red_defender.name as red_defender_name,
         blue_score, red_score, tg.created_timestamp 
        FROM team_game tg
        JOIN players p_blue_attacker
        ON tg.blue_attacker = p_blue_attacker.id
        JOIN players p_blue_defender
        ON tg.blue_defender = p_blue_defender.id
        JOIN players p_red_attacker
        ON tg.red_attacker = p_red_attacker.id
        JOIN players p_red_defender
        ON tg.red_defender = p_red_defender.id
        ORDER BY tg.created_timestamp DESC
        LIMIT 25
        """,
        cur=cur
    )

    return render_template(
        "team_games.html",
        recent_team_games=recent_team_games,
    )


@app.route("/add_player", methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        cur, con = get_cursor_and_connection()
        run_param_query("INSERT INTO players(name) VALUES (?)", (name,), cur=cur)
        con.commit()
        flash('User Added', 'success')
        return redirect(url_for("players"))
    return render_template("add_player.html")


@app.route("/register_solo_game", methods=['GET', 'POST'])
def register_solo_game():
    if request.method == 'POST':
        return add_solo_game_result(request)

    player_list = get_select_query_result("SELECT id, name FROM players")
    return render_template("register_solo_game.html", player_list=player_list)


def add_solo_game_result(request):
    blue_id = int(request.form['blue'])
    red_id = int(request.form['red'])
    blue_score = int(request.form['blue_score'])
    red_score = int(request.form['red_score'])
    went_under = "went_under" in request.form and request.form['went_under'] == "on"

    blue = Player(blue_id)
    blue.init_solo_rating()

    red = Player(red_id)
    red.init_solo_rating()

    game = SoloGame(
        id=None,
        blue=blue,
        red=red,
        blue_score=blue_score,
        red_score=red_score,
        went_under=went_under
    )

    try:
        _validate_solo_game_parameters(game)
    except AssertionError as e:
        flash(str(e))
        return redirect(request.url)

    cur, con = get_cursor_and_connection()

    game.insert_game_into_db(cur)
    rating.update_solo_rating(game.winner, game.loser)
    game.insert_rating_into_db(cur)

    con.commit()

    flash('Game Added', 'success')
    return redirect(url_for("solo_games"))


def _validate_solo_game_parameters(game: SoloGame):
    assert game.blue.id != game.red.id, "You can't play against yourself, dumbass"
    assert game.blue_score != game.red_score, "Ties are not allowed, keep playing"


@app.route("/register_team_game", methods=['GET', 'POST'])
def register_team_game():
    if request.method == 'POST':
        print(f"GOT {request.form}")
        return add_team_game_result(request)

    player_list = get_select_query_result("SELECT id, name FROM players")
    return render_template("register_team_game.html", player_list=player_list)


def add_team_game_result(request):
    blue_attacker_id = int(request.form['blue_attacker'])
    blue_defender_id = int(request.form['blue_defender'])
    red_attacker_id = int(request.form['red_attacker'])
    red_defender_id = int(request.form['red_defender'])
    blue_score = int(request.form['blue_score'])
    red_score = int(request.form['red_score'])
    went_under = "went_under" in request.form and request.form['went_under'] == "on"

    blue_attacker = Player(blue_attacker_id)
    blue_attacker.init_team_rating()
    blue_defender = Player(blue_defender_id)
    blue_defender.init_team_rating()

    red_attacker = Player(red_attacker_id)
    red_attacker.init_team_rating()
    red_defender = Player(red_defender_id)
    red_defender.init_team_rating()

    blue = Team(blue_attacker, blue_defender)
    red = Team(red_attacker, red_defender)

    game = TeamGame(
        id=None,
        blue=blue,
        red=red,
        blue_score=blue_score,
        red_score=red_score,
        went_under=went_under
    )

    try:
        _validate_team_game_parameters(game)
    except AssertionError as e:
        flash(str(e))
        return redirect(request.url)

    cur, con = get_cursor_and_connection()

    game.insert_game_into_db(cur)
    rating.update_team_rating(game.winner, game.loser)
    game.insert_rating_into_db(cur)

    con.commit()

    flash('Game Added', 'success')
    return redirect(url_for("team_games"))


def _validate_team_game_parameters(game: TeamGame):
    assert len(
        {
            game.red.attacker.id,
            game.red.defender.id,
            game.blue.attacker.id,
            game.blue.defender.id
        }
    ) == 4, "Players need to be distinct"
    assert game.blue_score != game.red_score, "Ties are not allowed"


@app.route("/delete_last_solo_game")
def delete_last_solo_game():

    if request.method == 'DELETE':
        cur, conn = get_cursor_and_connection()
        game_to_delete = fetch_one_query_result("SELECT id FROM solo_game ORDER BY updated_timestamp DESC LIMIT 1", cur=cur)
        if game_to_delete:
            game_id_to_delete = game_to_delete[0]

            run_param_query("DELETE FROM solo_game WHERE id=?", (game_id_to_delete,), cur=cur)
            run_param_query("DELETE FROM solo_ranking WHERE game_id=?", (game_id_to_delete,), cur=cur)

            conn.commit()


@app.route("/delete_last_team_game")
def delete_last_team_game():

    if request.method == 'DELETE':
        cur, conn = get_cursor_and_connection()
        game_to_delete = fetch_one_query_result("SELECT id FROM team_game ORDER BY updated_timestamp DESC LIMIT 1", cur=cur)
        if game_to_delete:
            game_id_to_delete = game_to_delete[0]

            run_param_query("DELETE FROM team_game WHERE id=?", (game_id_to_delete,), cur=cur)
            run_param_query("DELETE FROM team_ranking WHERE game_id=?", (game_id_to_delete,), cur=cur)

            conn.commit()


if __name__ == '__main__':
    app.run(debug=True)
