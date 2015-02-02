# -*- coding: utf-8-*-
import random
import re

WORDS = [_("MEANING"), _("OF"), _("LIFE")]


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, by relaying the
        meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    messages = [_("It's 42, you idiot."),
                _("It's 42. How many times do I have to tell you?")]

    message = random.choice(messages)

    mic.say(message)


def isValid(text):
    """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b', _('meaning of life'), r'\b', text, re.IGNORECASE))
