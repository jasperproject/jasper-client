# -*- coding: utf-8-*-
import datetime
import re
from client.app_utils import getTimezone

WORDS = [_("TIME")]


def handle(text, mic, profile):
    """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """

    tz = getTimezone(profile)
    now = datetime.datetime.now(tz=tz)
    mic.say(_("It is %s right now.") % now.strftime(_("%I %M %p")))


def isValid(text):
    """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r"\b" + _("time") + r"\b", text, re.IGNORECASE))
