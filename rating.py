from trueskill import Rating, rate, rate_1vs1

from model import Player, Team


def update_solo_rating(winner: Player, loser: Player) -> None:
    new_winner_rating, new_loser_rating = rate_1vs1(winner.solo_rating, loser.solo_rating)
    winner.solo_rating = new_winner_rating
    loser.solo_rating = new_loser_rating


def update_team_rating(winner: Team, loser: Team) -> None:
    (new_winner_attacker_rating, new_winner_defender_rating), (new_loser_attacker_rating, new_loser_defender_rating) = rate(
        [
            [winner.attacker.team_rating, winner.defender.team_rating],
            [loser.attacker.team_rating, loser.defender.team_rating]
        ]
    )

    winner.attacker.team_rating = new_winner_attacker_rating
    winner.defender.team_rating = new_winner_defender_rating
    loser.attacker.team_rating = new_loser_attacker_rating
    loser.defender.team_rating = new_loser_defender_rating

