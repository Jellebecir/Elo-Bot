from util.slack_client_util import get_slack_client

client = get_slack_client()


def handle_elo_bot_help(request_data):
    user_id = request_data.get('user_id')
    channel_id = request_data.get('channel_id')
    message = "Elo Bot to the rescue!\n\n" \
              "In short, Elo Bot is a Slack bot that can be installed in a channel. It then keeps track of games " \
              "played in said channel, and the rating of players in the channel. " \
              "This game could be table tennis or any other game with a binary outcome where 2 " \
              "players play against each other, like chess, pool or even fencing.\n\n" \
              "*Elo Bot Commands:*\n" \
              " - _*/beatme*_: This command is the key feature of Elo Bot that allows players to " \
              "report match results and update their ratings. When a player uses the 'beatme' command " \
              "with the name of their opponent written like *@opponent-name*, the bot records the outcome of the " \
              "match and updates the ratings of both players accordingly.\n" \
              " - _*/score*_: This command tells you the score between you and another player. " \
              "Simply write @their-name after the command and you'll get a message with the score.\n" \
              " - _*/leaderboard*_: This command shows you the current leaderboard in the channel.\n\n" \
              "*The Elo system*\n" \
              "The Elo ranking system is a method for calculating the relative skill levels of players " \
              "in two-player games such as chess. Each player has a rating, which is a number that represents " \
              "their skill level. When two players play a game, the winner's rating goes up and the loser's rating " \
              "goes down. The amount that the ratings change is based on the difference between the players' ratings " \
              "and the outcome of the game. The more evenly matched the players are, the less their ratings will " \
              "change. The more uneven the match, the more their ratings will change. This way, a player's rating " \
              "will go up _more_ if they beat someone who is rated higher than them, and it will go down _less_ " \
              "if they lose to someone who is rated lower."
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=message
    )
