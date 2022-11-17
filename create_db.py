from dataclasses import dataclass, field
import sqlite3 as sql
from typing import List

from utils import SQLITE_DB_PATH


@dataclass
class Column:
    name: str
    type: str


@dataclass
class Table:
    name: str
    columns: List[Column]
    additional_statement: List[str] = field(default_factory=list)

    def create_statement(self) -> str:
        return f"""
            CREATE TABLE {self.name} (
                {",".join([col.name + " " + col.type for col in self.columns])}
                {"," + ",".join(self.additional_statement) if self.additional_statement else ""}
            )
        """

    def drop_statement(self) -> str:
        return f"DROP TABLE IF EXISTS {self.name}"


players = Table(
    "players",
    [
        Column("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        Column("name", "TEXT UNIQUE NOT NULL"),
        Column("updated_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        Column("created_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
    ]
)

solo_ranking = Table(
    "solo_ranking",
    [
        Column("player_id", "INTEGER PRIMARY KEY"),
        Column("mu", "REAL NOT NULL"),
        Column("sigma", "REAL NOT NULL")
    ],
    ["FOREIGN KEY(player_id) REFERENCES players(id)"]
)

team_ranking = Table(
    "team_ranking",
    [
        Column("player_id", "INTEGER PRIMARY KEY"),
        Column("mu", "REAL NOT NULL"),
        Column("sigma", "REAL NOT NULL")
    ],
    ["FOREIGN KEY(player_id) REFERENCES players(id)"]
)

solo_game = Table(
    "solo_game",
    [
        Column("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        Column("player1", "INTEGER NOT NULL"),
        Column("player2", "INTEGER NOT NULL"),
        Column("player1_score", "INTEGER NOT NULL"),
        Column("player2_score", "INTEGER NOT NULL"),
        Column("updated_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"),
        Column("created_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"),
        Column("went_under", "BOOLEAN DEFAULT FALSE NOT NULL"),
    ],
    [
        "FOREIGN KEY(player1) REFERENCES players(id)",
        "FOREIGN KEY(player2) REFERENCES players(id)"
    ]
)

team_game = Table(
    "team_game",
    [
        Column("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        Column("team1_player1", "INTEGER NOT NULL"),
        Column("team1_player2", "INTEGER NOT NULL"),
        Column("team2_player1", "INTEGER NOT NULL"),
        Column("team2_player2", "INTEGER NOT NULL"),
        Column("team1_score", "INTEGER NOT NULL"),
        Column("team2_score", "INTEGER NOT NULL"),
        Column("updated_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"),
        Column("created_timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"),
        Column("went_under", "BOOLEAN DEFAULT FALSE NOT NULL"),
    ],
    [
        "FOREIGN KEY(team1_player1) REFERENCES players(id)",
        "FOREIGN KEY(team1_player2) REFERENCES players(id)",
        "FOREIGN KEY(team2_player1) REFERENCES players(id)",
        "FOREIGN KEY(team2_player2) REFERENCES players(id)"
    ]
)

tables = [players, solo_ranking, team_ranking, solo_game, team_game]


def init_db(reset=False) -> None:
    # connect to SQLite
    con = sql.connect(SQLITE_DB_PATH)

    # Create a Connection
    cur = con.cursor()

    if reset:
        for table in tables:
            cur.execute(table.drop_statement())

    for table in tables:
        cur.execute(table.create_statement())

    # commit changes
    con.commit()

    # close the connection
    con.close()


if __name__ == '__main__':
    init_db(True)
