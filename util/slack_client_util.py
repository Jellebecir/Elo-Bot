import os
import re
from pathlib import Path

import slack
from dotenv import load_dotenv

from util.custom_exceptions import \
    UserNotFoundException, \
    UserNotInChannelException, \
    DataRetrievalException, \
    InvalidUserProvidedException


env_path = Path('') / '.env'
load_dotenv(dotenv_path=env_path)
token = os.environ['TEST_SLACK_TOKEN']
client = slack.WebClient(token=token)

def get_slack_client():
    return client


def get_user_by_name(user_name, channel_id):
    channel_users = get_channel_users(channel_id=channel_id)
    for user in channel_users:
        if user['name'] == user_name:
            return user
    raise UserNotFoundException()


def is_user_in_channel(user_id, channel_id):
    client_response = client.conversations_members(channel=channel_id)
    if client_response['ok']:
        for member_id in client_response['members']:
            if member_id == user_id:
                return True
        raise UserNotInChannelException()
    else:
        raise DataRetrievalException()


def get_channel_users(channel_id):
    """
    Gets all user IDs in the channel
    :param channel_id: string representing the channel ID
    :return: array of user IDs (string)
    """
    client_response = client.conversations_members(channel=channel_id)
    if client_response['ok']:
        all_users = []
        for member_id in client_response['members']:
            user = get_user_by_id(member_id)
            all_users.append(user)
        return all_users
    else:
        raise DataRetrievalException()


def get_user_by_id(user_id):
    user_response = client.users_info(user=user_id)
    if user_response['ok']:
        return user_response['user']
    else:
        raise DataRetrievalException()


def get_user_name_by_id(user_id):
    user_info = get_user_by_id(user_id)
    return get_user_name(user_info)


def get_user_name(user):
    user_display_name = user['profile']['display_name']
    if not user_display_name:
        return user['profile']['real_name']
    else:
        return user_display_name


def parse_request_name(name):
    pattern = r'@(.+)'
    match = re.match(pattern, name.split(" ")[0])
    if match:
        return match.group(1)
    else:
        raise InvalidUserProvidedException()
