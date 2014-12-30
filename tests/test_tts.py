#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
from client import tts


class TestTTS(unittest.TestCase):
    def testTTS(self):
        tts_engine = tts.get_engine_by_slug('dummy-tts')
        tts_instance = tts_engine()
        tts_instance.say('This is a test.')
