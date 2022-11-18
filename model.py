import sqlite3
from dataclasses import dataclass
from typing import Optional, Union

from trueskill import Rating

from db_query import fetch_one_query_result, run_insert_query, run_many_insert_query


@dataclass
class Player:
    id: int
    solo_rating: Optional[Rating] = None
    team_rating: Optional[Rating] = None

    def init_solo_rating(self) -> None:
        if not self.solo_rating:
            res = fetch_one_query_result(
                """
                SELECT sr.mu, sr.sigma
                FROM solo_ranking sr
                JOIN solo_game sg
                ON sg.id = sr.game_id
                WHERE sr.player_id=?
                ORDER BY sg.created_timestamp DESC
                """,
                (self.id,)
            )

            self.solo_rating = Rating(*res) if res else Rating()

    def init_team_rating(self):
        if not self.team_rating:
            res = fetch_one_query_result(
                """
                SELECT tr.mu, tr.sigma
                FROM team_ranking tr
                JOIN team_game tg
                ON tg.id = tr.game_id
                WHERE tr.player_id=?
                ORDER BY tg.created_timestamp DESC
                """,
                (self.id,)
            )
            self.team_rating = Rating(*res) if res else Rating()


@dataclass
class Team:
    attacker: Player
    defender: Player


@dataclass
class Game:
    id: Optional[int]
    blue: Union[Player, Team]
    red: Union[Player, Team]
    blue_score: int
    red_score: int
    went_under: bool

    @property
    def winner(self) -> Union[Player, Team]:
        return self.blue if self.blue_score > self.red_score else self.red

    @property
    def loser(self) -> Union[Player, Team]:
        return self.blue if self.blue_score < self.red_score else self.red


@dataclass
class SoloGame(Game):
    blue: Player
    red: Player

    def insert_game_into_db(self, cur: sqlite3.Cursor) -> None:
        run_insert_query(
            """
            INSERT INTO solo_game(blue, red, blue_score, red_score, went_under)
            VALUES (?,?,?,?,?)
            """,
            (self.blue.id, self.red.id, self.blue_score, self.red_score, self.went_under),
            cur
        )
        self.id = cur.lastrowid

    def insert_rating_into_db(self, cur: sqlite3.Cursor) -> None:
        run_many_insert_query(
            """
            INSERT INTO solo_ranking (player_id, mu, sigma, game_id)
            VALUES (?, ?, ?, ?)
            """,
            [
                (self.blue.id, self.blue.solo_rating.mu, self.blue.solo_rating.sigma, self.id),
                (self.red.id, self.red.solo_rating.mu, self.red.solo_rating.sigma, self.id)
            ],
            cur
        )


@dataclass
class TeamGame(Game):
    blue: Team
    red: Team

    def insert_game_into_db(self, cur: sqlite3.Cursor) -> None:
        run_insert_query(
            """
            INSERT INTO team_game(
                blue_attacker,
                blue_defender,
                red_attacker,
                red_defender,
                blue_score,
                red_score,
                went_under
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                self.blue.attacker.id,
                self.blue.defender.id,
                self.red.attacker.id,
                self.red.defender.id,
                self.blue_score,
                self.red_score,
                self.went_under
            ),
            cur
        )
        self.id = cur.lastrowid

    def insert_rating_into_db(self, cur: sqlite3.Cursor) -> None:
        print(f"INSERTING RATINGS FOR {self}")
        run_many_insert_query(
            """
            INSERT INTO team_ranking (player_id, mu, sigma, game_id)
            VALUES (?, ?, ?, ?)
            """,
            [
                (self.blue.attacker.id, self.blue.attacker.team_rating.mu, self.blue.attacker.team_rating.sigma, self.id),
                (self.blue.defender.id, self.blue.defender.team_rating.mu, self.blue.defender.team_rating.sigma, self.id),
                (self.red.attacker.id, self.red.attacker.team_rating.mu, self.red.attacker.team_rating.sigma, self.id),
                (self.red.defender.id, self.red.defender.team_rating.mu, self.red.defender.team_rating.sigma, self.id),
            ],
            cur
        )
