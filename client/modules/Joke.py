import random
import re

WORDS = ["JOKE", "KNOCK KNOCK"]


def getRandomJoke(filename="JOKES.txt"):
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
    joke = random.choice(jokes)
    return joke


def handle(text, sender, receiver, profile):
    """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    joke = getRandomJoke()

    sender.say("Knock knock")

    def firstLine(text):
        sender.say(joke[0])

        def punchLine(text):
            sender.say(joke[1])

        punchLine(receiver.activeListen())

    firstLine(receiver.activeListen())


def isValid(text):
    """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bjoke\b', text, re.IGNORECASE))
