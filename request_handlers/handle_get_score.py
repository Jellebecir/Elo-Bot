import os
from util.custom_exceptions import NoUserProvidedException, SameUserProvidedException
from util.slack_client_util import get_slack_client, parse_request_name, get_user_by_name, get_user_name
from texttable import Texttable

client = get_slack_client()

bot_id = os.environ['BOT_ID']


class GetScoreHandler:
    def __init__(self, database, request_data):
        self.database = database
        self.channel_id = request_data.get('channel_id')
        self.user_id = request_data.get('user_id')
        self.opponent_name = parse_request_name(request_data.get('text'))

        if not self.opponent_name:
            raise NoUserProvidedException()

        opponent_user_info = get_user_by_name(self.opponent_name, self.channel_id)
        self.opponent_id = opponent_user_info['id']

        if self.opponent_id == self.user_id:
            raise SameUserProvidedException()

        self.opponent_display_name = get_user_name(opponent_user_info)
        self.score = None

    def handle_get_score(self):
        if self.user_id == bot_id:
            client.chat_postEphemeral(
                channel=self.channel_id,
                user=self.user_id,
                text="I don't play so i'm not keeping score between us"
            )

        self.get_score()
        message = self.get_score_table()
        client.chat_postEphemeral(
            channel=self.channel_id,
            user=self.user_id,
            text=message
        )

    def get_score(self):
        self.score = self.database.get_history_between_players(self.user_id, self.opponent_id, self.channel_id)

    def get_score_table(self):
        header = ["Player", "Wins", " "]
        rows = [header]
        for player_id in list(self.score.keys()):
            row = []

            if player_id == self.user_id:
                row.append("You")
            else:
                row.append(self.opponent_display_name)

            row.append(self.score[player_id])
            row.append(self.winner_indicator(player_id))
            rows.append(row)
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.add_rows(rows, False)
        return f"Your score against {self.opponent_display_name}\n```" + table.draw() + "```"

    def winner_indicator(self, player_id):
        if self.player_has_highest_score(player_id):
            return '👑'
        else:
            return ''

    def player_has_highest_score(self, player_id):
        value = self.score[player_id]
        highest_value = max(self.score.values())

        if value == highest_value and list(self.score.values()).count(value) == 1:
            return True
        else:
            return False


