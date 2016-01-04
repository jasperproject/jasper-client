# -*- coding: utf-8 -*-
from sys import maxint
import random
from jasper import plugin


class UnclearPlugin(plugin.SpeechHandlerPlugin):
    def get_priority(self):
        return -(maxint + 1)

    def get_phrases(self):
        return []

    def handle(self, text, mic):
        """
        Reports that the user has unclear or unusable input.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """

        messages = [
            self.gettext("I'm sorry, could you repeat that?"),
            self.gettext("My apologies, could you try saying that again?"),
            self.gettext("Say that again?"),
            self.gettext("I beg your pardon?")
        ]

        message = random.choice(messages)

        mic.say(message)

    def is_valid(self, text):
        return True
