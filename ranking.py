import sqlite3
from typing import Tuple

import trueskill as ts

from db_query import fetch_one_query_result, get_select_query_result, run_insert_query, run_many_insert_query


def get_initial_rating() -> ts.Rating:
    return ts.Rating()


def update_solo_ranking(winner_id: int, loser_id: int) -> None:
    winner_mu, winner_sigma = fetch_one_query_result("SELECT mu, sigma FROM solo_ranking WHERE player_id=?", (winner_id,))
    loser_mu, loser_sigma = fetch_one_query_result("SELECT mu, sigma FROM solo_ranking WHERE player_id=?", (loser_id,))

    winner_rating = ts.Rating(winner_mu, winner_sigma)
    loser_rating = ts.Rating(loser_mu, loser_sigma)

    new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating)

    run_many_insert_query(
        "INSERT OR REPLACE INTO solo_ranking (player_id, mu, sigma) VALUES (?, ?, ?)",
        [
            (winner_id, new_winner_rating.mu, new_winner_rating.sigma),
            (loser_id, new_loser_rating.mu, new_loser_rating.sigma)
        ]
    )


def update_team_ranking(winner_team: Tuple[int, int], loser_team: Tuple[int, int]) -> None:
    winner1_mu, winner1_sigma = fetch_one_query_result("""SELECT mu, sigma FROM team_ranking WHERE player_id=?""", (winner_team[0],))
    winner2_mu, winner2_sigma = fetch_one_query_result("""SELECT mu, sigma FROM team_ranking WHERE player_id=?""", (winner_team[1],))

    loser1_mu, loser1_sigma = fetch_one_query_result("""SELECT mu, sigma FROM team_ranking WHERE player_id=?""", (loser_team[0],))
    loser2_mu, loser2_sigma = fetch_one_query_result("""SELECT mu, sigma FROM team_ranking WHERE player_id=?""", (loser_team[1],))

    winner_rating = [ts.Rating(winner1_mu, winner1_sigma), ts.Rating(winner2_mu, winner2_sigma)]
    loser_rating = [ts.Rating(loser1_mu, loser1_sigma), ts.Rating(loser2_mu, loser2_sigma)]

    (new_winner1_rating, new_winner2_rating), (new_loser1_rating, new_loser2_rating) = ts.rate([winner_rating, loser_rating])

    run_many_insert_query(
        "INSERT OR REPLACE INTO team_ranking (player_id, mu, sigma) VALUES (?, ?, ?)",
        [
            (winner_team[0], new_winner1_rating.mu, new_winner1_rating.sigma),
            (winner_team[1], new_winner2_rating.mu, new_winner2_rating.sigma),
            (loser_team[0], new_loser1_rating.mu, new_loser1_rating.sigma),
            (loser_team[1], new_loser2_rating.mu, new_loser2_rating.sigma),
        ]
    )

