__author__ = 'seanfitz'


class Receiver(object):
    prev = None

    def new(self, lmd, dictd, lmd_persona, dictd_persona):
        return Receiver(lmd, dictd, lmd_persona, dictd_persona)

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