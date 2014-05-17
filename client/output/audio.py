__author__ = 'seanfitz'
import alteration
import json
import os

class Sender(object):
    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)

        os.system("espeak " + json.dumps(phrase) + OPTIONS)
        os.system("aplay -D hw:1,0 say.wav")