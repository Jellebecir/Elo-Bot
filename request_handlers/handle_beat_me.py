import asyncio
import os
import sys
from database.db_connector import insert_match, get_user_ranking
from util.custom_exceptions import \
    NoUserProvidedException, \
    EloBotAsUserException, \
    SameUserProvidedException, \
    BeatMeCommandException, \
    UserNotFoundException
from util.calculate_elo import calculate_new_ratings
from util.slack_client_util import \
    is_user_in_channel, \
    get_user_by_name, \
    get_slack_client, \
    get_user_by_id, \
    get_user_name, \
    parse_request_name, \
    get_user_name_by_id

bot_id = os.environ['BOT_ID']
token = os.environ['SLACK_TOKEN']
client = get_slack_client()


class BeatMeHandler:
    def __init__(self, database, request_data):
        self.database = database
        self.loser_id = request_data.get('user_id')
        self.channel_id = request_data.get('channel_id')
        try:
            winner_name = parse_request_name(request_data.get('text'))
            self.winner_id = get_user_by_name(winner_name, self.channel_id)['id']
        except BeatMeCommandException as error:
            client.chat_postEphemeral(
                channel=self.channel_id,
                user=self.loser_id,
                text=error.message
            )

    def async_run_beat_me(self):
        """
        Starts async run of /beatme request handler
        :return: None
        """
        asyncio.run(
            self.create_beat_me_task()
        )

    async def create_beat_me_task(self):
        """
        Creates asynchronous task of handling the request data. This is because slack requires a resonse within 3000ms
        and this function takes more than 3 seconds.
        :return: None
        """
        loop = asyncio.get_event_loop()
        loop.create_task(
            self.beat_me_task_wrapper()
        )

    async def beat_me_task_wrapper(self):
        try:
            return await self.handle_beat_me()
        except BeatMeCommandException as error:
            client.chat_postEphemeral(
                channel=self.channel_id,
                user=self.loser_id,
                text=error.message
            )

    async def handle_beat_me(self):

        if not self.winner_id:
            raise NoUserProvidedException()

        if self.winner_id == bot_id:
            raise EloBotAsUserException()

        if self.winner_id == self.loser_id:
            raise SameUserProvidedException()

        if self.winner_id and is_user_in_channel(self.winner_id, self.channel_id):
            with self.database.connection_pool.get_connection() as connection:
                insert_match(
                    self.winner_id,
                    self.loser_id,
                    self.channel_id,
                    connection
                )
                self.update_user_rankings(connection)
                self.send_confirmation_to_winner(connection)
                self.send_confirmation_to_loser(connection)
                connection.commit()
        else:
            # TODO Raise correct Exception
            raise UserNotFoundException()

    def update_user_rankings(self, connection):
        # Get old rankings
        winner_old_ranking = get_user_ranking(self.winner_id, self.channel_id, connection)
        loser_old_ranking = get_user_ranking(self.loser_id, self.channel_id, connection)
        # Calculate new rankings
        new_rankings = calculate_new_ratings(winner_old_ranking, loser_old_ranking)
        # Update rankings in database
        self.database.update_user_ranking(self.winner_id, self.channel_id, new_rankings['winner'])
        self.database.update_user_ranking(self.loser_id, self.channel_id, new_rankings['loser'])

    def send_confirmation_to_winner(self, connection):
        rank = get_user_ranking(self.winner_id, self.channel_id, connection)
        opponent = get_user_name(get_user_by_id(self.loser_id))
        message = f"Congratulations on your victory against {opponent} 🏆\nYour new rank is {rank}"
        client.chat_postEphemeral(
            token=token,
            channel=self.channel_id,
            text=message,
            user=self.winner_id
        )
        print(" - SENT WIN CONFIRMATION TO {}".format(self.winner_id))

    def send_confirmation_to_loser(self, connection):
        rank = get_user_ranking(self.loser_id, self.channel_id, connection)
        opponent = get_user_name_by_id(self.winner_id)
        message = f"I'm sorry you lost to {opponent} 😢\nYour new rank is {rank}"
        client.chat_postEphemeral(
            token=token,
            channel=self.channel_id,
            text=message,
            user=self.loser_id
        )
        print(" - SENT LOSS CONFIRMATION TO {}".format(self.loser_id))





