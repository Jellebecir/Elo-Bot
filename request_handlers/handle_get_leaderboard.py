import datetime
import sys
import mysql.connector.errors
import os
from util.slack_client_util import get_user_name_by_id, get_slack_client
from texttable import Texttable

token = os.environ['SLACK_TOKEN']
client = get_slack_client()


def handle_get_leaderboard(data, database):
    print(" - GETTING LEADERBOARD...")
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    try:
        leaderboard = database.get_channel_leaderboard2(channel_id)
        table = get_leaderboard_table(leaderboard, user_id)
        client.chat_postEphemeral(
            channel=channel_id,
            text=table,
            user=user_id
        )
    except mysql.connector.errors.ProgrammingError as err:
        print("### Error in handle_get_leaderboard: ", err, file=sys.stderr)


def get_leaderboard_table(leaderboard, user_id):
    header = ["Rank", "Name", "Wins", "Losses", "Rating"]
    parsed_rows = []
    # TODO if leaderboard is emtpy post message that users will need to play games
    for i, row in enumerate(leaderboard):
        rank = i + 1
        parsed_row = parse_leaderboard_row(row, rank, user_id)
        parsed_rows.append(parsed_row)
    return create_table(header, parsed_rows)


def create_table(header, rows):
    table = Texttable()
    set_table_styling(table)
    set_table_content(table, header, rows)
    table_string = table.draw().replace("=", "")

    medal_count = len(rows) if len(rows) <= 3 else 3
    table_string = set_table_rank_medals(table_string, medal_count)
    return "```" + table_string + "```"


def set_table_styling(table):
    table.set_cols_align(["l" for i in range(5)])
    table.set_cols_valign(["m" for i in range(5)])
    table.set_deco(Texttable.HEADER)
    table.set_header_align(["l" for i in range(5)])


def set_table_content(table, header, rows):
    table.header(header)
    table.add_rows(rows, header=False)


def set_table_rank_medals(table_string, medal_count):
    medals = ["🥇", "🥈", "🥉"]
    return table_string.format(*[medals[i] for i in range(medal_count)])\



def parse_leaderboard_row(row, rank, user_id):
    row_user_id = row[0]
    if row_user_id == user_id:
        user_name = "You"
    else:
        user_name = get_user_name_by_id(row_user_id)
    row[0] = user_name
    add_rank_to_row(rank, row)
    return row


def add_rank_to_row(rank, row):
    if rank < 4:
        row.insert(0, "{}")
    else:
        row.insert(0, rank)
