# -*- coding: utf-8-*-
import random
import re
from client import jasperpath
from client import plugin


def get_jokes(filename=jasperpath.data('text', 'JOKES.txt')):
    jokeFile = open(filename, "r")
    jokes = []
    start = ""
    end = ""
    for line in jokeFile.readlines():
        line = line.replace("\n", "")

        if start == "":
            start = line
            continue

        if end == "":
            end = line
            continue

        jokes.append((start, end))
        start = ""
        end = ""

    jokes.append((start, end))
    return jokes


class JokePlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return ["JOKE", "KNOCK KNOCK"]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        joke = random.choice(get_jokes())

        mic.say("Knock knock")
        mic.active_listen()
        mic.say(joke[0])
        mic.active_listen()
        mic.say(joke[1])

    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return bool(re.search(r'\bjoke\b', text, re.IGNORECASE))
