# -*- coding: utf-8-*-
import datetime
import re
import facebook
from client.app_utils import getTimezone

WORDS = ["BIRTHDAY"]


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, by listing the user's
        Facebook friends with birthdays today.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    oauth_access_token = profile['keys']["FB_TOKEN"]

    graph = facebook.GraphAPI(oauth_access_token)

    try:
        results = graph.request("me/friends",
                                args={'fields': 'id,name,birthday'})
    except facebook.GraphAPIError:
        mic.say("I have not been authorized to query your Facebook. If you " +
                "would like to check birthdays in the future, please visit " +
                "the Jasper dashboard.")
        return
    except:
        mic.say(
            "I apologize, there's a problem with that service at the moment.")
        return

    needle = datetime.datetime.now(tz=getTimezone(profile)).strftime("%m/%d")

    people = []
    for person in results['data']:
        try:
            if needle in person['birthday']:
                people.append(person['name'])
        except:
            continue

    if len(people) > 0:
        if len(people) == 1:
            output = people[0] + " has a birthday today."
        else:
            output = "Your friends with birthdays today are " + \
                ", ".join(people[:-1]) + " and " + people[-1] + "."
    else:
        output = "None of your friends have birthdays today."

    mic.say(output)


def isValid(text):
    """
        Returns True if the input is related to birthdays.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'birthday', text, re.IGNORECASE))
