import re
from facebook import *


WORDS = ["FACEBOOK", "NOTIFICATION"]


def handle(text, sender, receiver, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the user's Facebook notifications, including a count and details
        related to each individual notification.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    oauth_access_token = profile['keys']['FB_TOKEN']

    graph = GraphAPI(oauth_access_token)

    try:
        results = graph.request("me/notifications")
    except GraphAPIError:
        sender.say(
            "I have not been authorized to query your Facebook. If you would like to check your notifications in the future, please visit the Jasper dashboard.")
        return
    except:
        sender.say(
            "I apologize, there's a problem with that service at the moment.")

    if not len(results['data']):
        sender.say("You have no Facebook notifications. ")
        return

    updates = []
    for notification in results['data']:
        updates.append(notification['title'])

    count = len(results['data'])
    sender.say("You have " + str(count) +
            " Facebook notifications. " + " ".join(updates) + ". ")

    return


def isValid(text):
    """
        Returns True if the input is related to Facebook notifications.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bnotification|Facebook\b', text, re.IGNORECASE))
