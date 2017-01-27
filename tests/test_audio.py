#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
from client import jasperpath
from client.modules import Life
from jasper import Jasper

DEFAULT_PROFILE = {
    'prefers_email': False,
    'location': 'Cape Town',
    'timezone': 'US/Eastern',
    'phone_number': '012344321'
}

WAKE_AUDIO_FILE = jasperpath.join(jasperpath.TEST_AUDIO_PATH, 'jasper.wav')

# set input file path to mic.audio_input
# read output text from mic.text_output


class TestAudio(unittest.TestCase):

    def setUp(self):
        self.profile = DEFAULT_PROFILE
        self.send = False
        self.persona = "Jasper"
        self.jasper = Jasper()
        self.mic = self.jasper.mic

    def testLife(self):
        # Wake up
        self.mic.audio_input = WAKE_AUDIO_FILE
        threshold, transcribed = self.mic.passiveListen(self.persona)
        print(transcribed)

        # Run the meaning of life module
        self.mic.audio_input = jasperpath.join(jasperpath.TEST_AUDIO_PATH,
                                               'meaning_of_life.wav')
        transcribed = self.mic.activeListen()
        print(transcribed)
        Life.handle(transcribed, self.mic, self.profile)

        print(self.mic.text_output)
        self.assertTrue("42" in self.mic.text_output)
