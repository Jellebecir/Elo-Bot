import calendar
import datetime
import time
from request_handlers.handle_get_leaderboard import get_leaderboard_table
from util.slack_client_util import get_slack_client


def monthly_leaderboard_listener(database):
    while True:
        today = datetime.date.today()

        # Check if today is the last day of the month
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        if today.day == last_day_of_month:
            post_leaderboard_to_all_channels(database)

        time.sleep(24*60*60)  # wait for 24 hours


def post_leaderboard_to_all_channels(database):
    client = get_slack_client()
    channel_ids = database.get_all_channel_ids()
    for channel_id in channel_ids:
        leaderboard = database.get_channel_leaderboard(channel_id)
        table = get_leaderboard_table(leaderboard, '')  # no user id so all names will be displayed
        client.chat_postMessage(
            channel=channel_id,
            text=table
        )
