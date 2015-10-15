# -*- coding: utf-8-*-
from sys import maxint
import random
from client import plugin


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

        messages = ["I'm sorry, could you repeat that?",
                    "My apologies, could you try saying that again?",
                    "Say that again?", "I beg your pardon?"]

        message = random.choice(messages)

        mic.say(message)

    def is_valid(self, text):
        return True
