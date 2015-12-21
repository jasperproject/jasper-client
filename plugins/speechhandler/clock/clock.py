# -*- coding: utf-8 -*-
import datetime
from client.app_utils import get_timezone
from client import plugin


class ClockPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("TIME")]

    def handle(self, text, mic):
        """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """

        tz = get_timezone(self.profile)
        now = datetime.datetime.now(tz=tz)
        if now.minute == 0:
            fmt = "It is {t:%l} {t:%P} right now."
        else:
            fmt = "It is {t:%l}:{t.minute} {t:%P} right now."
        mic.say(self.gettext(fmt).format(t=now))

    def is_valid(self, text):
        """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
