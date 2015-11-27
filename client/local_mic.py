# -*- coding: utf-8 -*-
"""
A drop-in replacement for the Mic class that allows for all I/O to occur
over the terminal. Useful for debugging. Unlike with the typical Mic
implementation, Jasper is always active listening with local_mic.
"""


class Mic:
    prev = None

    def __init__(self, *args, **kwargs):
        return

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
        input = raw_input("YOU: ")
        self.prev = input
        return input
    # Jasper is always active listening via command line for the local mic.
    listen = active_listen

    def say(self, phrase, OPTIONS=None):
        print("JASPER: %s" % phrase)
