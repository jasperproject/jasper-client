"""
A drop-in replacement for the Mic class that allows for all I/O to occur
over the terminal. Useful for debugging. Unlike with the typical Mic
implementation, Jasper is always active listening with local_mic.
"""


class Mic:
    prev = None

    def __init__(self, lmd, dictd, lmd_persona, dictd_persona):
        return

    def passiveListen(self, PERSONA):
        return True, "JASPER"

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        if not LISTEN:
            return self.prev

        input = raw_input("YOU: ")
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        print "JASPER: " + phrase
