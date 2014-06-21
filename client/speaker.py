"""
A Speaker handles audio output from Jasper to the user
"""
import os, json

class PiSpeaker:

    @classmethod
    def isAvailable(cls):
        return os.system("which espeak") == 0

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        os.system("espeak " + json.dumps(phrase) + OPTIONS)
        self.playSound("say.wav")

    def playSound(self, filename):
        os.system("aplay -D hw:1,0 " + filename)

class MacSpeaker:

    @classmethod
    def isAvailable(cls):
        return os.system("which say") == 0

    def say(self, phrase):
        os.system("say " + phrase)

    def playSound(self, filename):
        os.system("afplay " + filename)

def newSpeaker():
    for cls in [PiSpeaker, MacSpeaker]:
        if cls.isAvailable():
            return cls()
    raise ValueError("Platform is not supported")
