import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from request_handlers.handle_beat_me import BeatMeHandler
from util.custom_exceptions import InvalidUserProvidedException, NoUserProvidedException
from request_handlers.handle_elo_bot_help import handle_elo_bot_help
from request_handlers.handle_get_score import GetScoreHandler
from util.slack_client_util import get_channel_users, get_slack_client, get_user_name_by_id
from request_handlers.handle_get_leaderboard import handle_get_leaderboard
import asyncio
import multiprocessing
from database.db_connector import DBConnector, insert_user, create_channel_table, get_user_ranking, user_in_table

signing_secret = os.environ['SIGNING_SECRET']
token = os.environ['SLACK_TOKEN']
bot_id = os.environ['BOT_ID']

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(signing_secret, '/slack/events', app)

client = get_slack_client()

database_connector = DBConnector()


# TODO make sure bot only responds to commands and events in channels where bot is a member


@slack_event_adapter.on('member_joined_channel')
def handle_member_joined(payload):
    """
    Handle user joining channel by adding them to the database and giving them the base ranking of 1200
    :param payload: Event data
    :return: void
    """
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')

    if user_id == bot_id:
        event_handling_thread = multiprocessing.Process(
            target=handle_bot_joined_channel_process,
            args=(channel_id,)
        )
        event_handling_thread.start()
    else:
        with database_connector.connection_pool.get_connection() as connection:
            user_name = get_user_name_by_id(user_id)
            user_rating = get_user_ranking(user_id, channel_id, connection)
            if user_in_table(user_id, channel_id, connection):
                message = f"Welcome back {user_name}!\n" \
                          f"Even though you left, we kept your records." \
                          f"Your rating in this channel is {user_rating}."
            else:
                insert_user(user_id, channel_id, connection)
                connection.commit()
                message = "Hey there, welcome to this Slack channel!\n\n" \
                          "I'm Elo Bot. I keep track of the matches played in this channel. " \
                          "Any time you play a match against someone, " \
                          "your rating will be updated based on the outcome " \
                          "of the game and the rating of your opponent. " \
                          "Over time, you'll see how you're progressing and " \
                          "how you stack up against other players in the channel.\n\n" \
                          "To get started, challenge someone to a game and let me take care of the rest! " \
                          "You can find out how with the _/elo-bot-help_ command. " \
                          "Here you'll see a list of all bot commands and a more extensive " \
                          "explanation of the Elo system.\n\n" \
                          "If you have any other questions or feedback, feel free to send Jelle a message."
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=message
            )


def handle_bot_joined_channel_process(channel_id):
    asyncio.run(
        handle_bot_joined_channel(channel_id)
    )


async def handle_bot_joined_channel(channel_id):
    with database_connector.connection_pool.get_connection() as connection:
        create_channel_table(channel_id, connection)
        users = get_channel_users(channel_id)
        for user in users:
            if not user['id'] == bot_id:
                insert_user(user['id'], channel_id, connection)


@app.route('/beatme', methods=['POST'])
def handle_match():
    """
    Creates thread for handling the request but 'instantly' sends 202 response that the request has been accepted
    :return: http response
    """
    request_data = request.form
    beat_me_handler = BeatMeHandler(database_connector, request_data)
    multiprocessing.Process(
        target=beat_me_handler.async_run_beat_me
    ).start()
    return Response(), 202


@app.route('/leaderboard', methods=['POST'])
def get_leaderboard():
    """
    Handles the /leaderboard request
    :return: http response
    """
    data = request.form
    multiprocessing.Process(
        target=handle_get_leaderboard,
        args=(data, database_connector)
    ).start()
    return Response(), 200


@app.route('/score', methods=["POST"])
def get_score():
    data = request.form
    try:
        get_score_handler = GetScoreHandler(database_connector, data)
        multiprocessing.Process(
            target=get_score_handler.handle_get_score
        ).start()
        return Response(), 200
    except InvalidUserProvidedException:
        client.chat_postEphemeral(
            channel=data.get('channel_id'),
            user=data.get('user_id'),
            text="You tried to get a score but provided an invalid user. "
                 "Please provide a user name like this '/score @some-user'"
        )
        return Response(), 400
    except NoUserProvidedException:
        client.chat_postEphemeral(
            channel=data.get('channel_id'),
            user=data.get('user_id'),
            text="You tried to get a score but provided no user. "
                 "Please provide a user name like this '/score @some-user'"
        )


@app.route('/elo-bot-help', methods=["POST"])
def handle_get_help():
    data = request.form
    handle_elo_bot_help(data)
    return Response(), 200


# monthly_leaderboard_listener_thread = threading.Thread(
#     target=monthly_leaderboard_listener
# )
# monthly_leaderboard_listener_thread.start()


if __name__ == "__main__":
    app.run(debug=True)
