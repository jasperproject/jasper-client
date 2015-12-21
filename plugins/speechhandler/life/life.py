# -*- coding: utf-8 -*-
import random
from client import plugin


class MeaningOfLifePlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("MEANING OF LIFE")]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by relaying the
        meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        messages = [
            self.gettext("It's 42, you idiot."),
            self.gettext("It's 42. How many times do I have to tell you?")
        ]

        message = random.choice(messages)

        mic.say(message)

    def is_valid(self, text):
        """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
