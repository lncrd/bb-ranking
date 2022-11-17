import sqlite3
import trueskill as ts
from db_query import fetch_one_query_result, get_select_query_result, run_insert_query


def update_solo_ranking(winner_id: int, loser_id: int) -> None:
    winner_result = fetch_one_query_result("""SELECT mu, sigma FROM solo_ranking WHERE player_id=?""", (winner_id,))
    if winner_result:
        winner_mu, winner_sigma = winner_result

    loser_result = fetch_one_query_result("""SELECT mu, sigma FROM solo_ranking WHERE player_id=?""", (loser_id,))
    if loser_result:
        loser_mu, loser_sigma = loser_result

    winner_rating = ts.Rating() if not winner_result else ts.Rating(winner_mu, winner_sigma)
    loser_rating = ts.Rating() if not loser_result else ts.Rating(loser_mu, loser_sigma)

    new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating)

    run_insert_query(
        """
        INSERT OR REPLACE INTO solo_ranking (player_id, mu, sigma) VALUES (?, ?, ?)
        """,
        (
            winner_id,
            new_winner_rating.mu,
            new_winner_rating.sigma
        )
    )

    run_insert_query(
        """
        INSERT OR REPLACE INTO solo_ranking (player_id, mu, sigma) VALUES (?, ?, ?)
        """,
        (
            loser_id,
            new_loser_rating.mu,
            new_loser_rating.sigma
        )
    )


def update_team_ranking(winner_id: int, loser_id: int) -> None:
    winner_result = fetch_one_query_result("""SELECT mu, sigma FROM solo_ranking WHERE player_id=?""", (winner_id,))
    if winner_result:
        winner_mu, winner_sigma = winner_result

    loser_result = fetch_one_query_result("""SELECT mu, sigma FROM solo_ranking WHERE player_id=?""", (loser_id,))
    if loser_result:
        loser_mu, loser_sigma = loser_result

    winner_rating = ts.Rating() if not winner_result else ts.Rating(winner_mu, winner_sigma)
    loser_rating = ts.Rating() if not loser_result else ts.Rating(loser_mu, loser_sigma)

    new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating)

    run_insert_query(
        """
        INSERT OR REPLACE INTO solo_ranking (player_id, mu, sigma) VALUES (?, ?, ?)
        """,
        (
            winner_id,
            new_winner_rating.mu,
            new_winner_rating.sigma
        )
    )

    run_insert_query(
        """
        INSERT OR REPLACE INTO solo_ranking (player_id, mu, sigma) VALUES (?, ?, ?)
        """,
        (
            loser_id,
            new_loser_rating.mu,
            new_loser_rating.sigma
        )
    )
