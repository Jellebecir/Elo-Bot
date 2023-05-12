import math


def calculate_new_ratings(winner_old_rating, loser_old_rating):
    # Constants
    k = 32  # K-factor

    # Calculate expected scores
    winner_expected = 1 / (1 + math.pow(10, (loser_old_rating - winner_old_rating) / 400))
    loser_expected = 1 / (1 + math.pow(10, (winner_old_rating - loser_old_rating) / 400))

    # Calculate new ratings
    winner_new_rating = winner_old_rating + k * (1 - winner_expected)
    loser_new_rating = loser_old_rating + k * (0 - loser_expected)

    return {'winner': winner_new_rating, 'loser': loser_new_rating}
