# -*- coding: utf-8 -*-
"""
A drop-in replacement for the Mic class that allows for all I/O to occur
over the terminal. Useful for debugging. Unlike with the typical Mic
implementation, Jasper is always active listening with local_mic.
"""


class Mic(object):
    prev = None

    def __init__(self, *args, **kwargs):
        return

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
        input = raw_input("YOU: ")
        self.prev = input
        return [input]

    def listen(self):
        return self.active_listen(timeout=3)

    def say(self, phrase, OPTIONS=None):
        print("JASPER: %s" % phrase)

    def ask(self, question):
        """
            Asks a questions and then returns the response

            Arguments:
            question -- the question to ask
        """
        self.say(question)
        return self.active_listen()
