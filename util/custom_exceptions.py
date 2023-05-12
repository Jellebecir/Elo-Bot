class BeatMeCommandException(Exception):
    def __init__(self):
        self.message = ""


class NoUserProvidedException(BeatMeCommandException):
    def __init__(self):
        self.message = "No user was provided. Please provide a user with the command like this: '/beatme @Elo Me'."


class EloBotAsUserException(BeatMeCommandException):
    def __init__(self):
        self.message = "Impossible, you can't beat me"


class InvalidUserProvidedException(BeatMeCommandException):
    def __init__(self):
        self.message = "An invalid user was provided. Please provide a user like '/beatme @Elo Me'"


class SameUserProvidedException(BeatMeCommandException):
    def __init__(self):
        self.message = "Very sneaky. You can't play against yourself! Go find a buddy to play with."


class UserNotFoundException(BeatMeCommandException):
    def __init__(self):
        self.message = "No user by that name was found. " \
                       "Make sure they are in this channel " \
                       "and that you spelled their name correctly."


class UserNotInChannelException(BeatMeCommandException):
    def __init__(self):
        self.message = "No user by that name was found in this channel."


class DataRetrievalException(BeatMeCommandException):
    def __init__(self):
        self.message = "Oops, something went wrong when trying to retrieve some data. Better luck next time :)"

