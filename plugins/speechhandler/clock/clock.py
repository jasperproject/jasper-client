# -*- coding: utf-8-*-
import datetime
import re
from client.app_utils import get_timezone
from client import plugin
from semantic.dates import DateService


class ClockPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return ["TIME"]

    def handle(self, text, mic):
        """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """

        tz = get_timezone(self.profile)
        now = datetime.datetime.now(tz=tz)
        service = DateService()
        response = service.convertTime(now)
        mic.say("It is %s right now." % response)

    def is_valid(self, text):
        """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return bool(re.search(r'\btime\b', text, re.IGNORECASE))
