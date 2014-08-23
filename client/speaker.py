"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    isAvailable - returns True if the platform supports this implementation
"""
import os
import json


class eSpeakSpeaker:

    """
    Uses the eSpeak speech synthesizer included in the Jasper disk image
    """
    @classmethod
    def isAvailable(cls):
        return os.system("which espeak") == 0

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        os.system("espeak " + json.dumps(phrase) + OPTIONS)
        self.play("say.wav")

    def play(self, filename):
        os.system("aplay -D hw:1,0 " + filename)


class saySpeaker:

    """
    Uses the OS X built-in 'say' command
    """

    @classmethod
    def isAvailable(cls):
        return os.system("which say") == 0

    def shellquote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def say(self, phrase):
        os.system("say " + self.shellquote(phrase))

    def play(self, filename):
        os.system("afplay " + filename)


def newSpeaker():
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    for cls in [eSpeakSpeaker, saySpeaker]:
        if cls.isAvailable():
            return cls()
    raise ValueError("Platform is not supported")
