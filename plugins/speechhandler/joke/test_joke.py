# -*- coding: utf-8 -*-
import unittest
import os.path
from jasper import testutils
from . import joke


class TestJokePlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(
            os.path.dirname(joke.__file__))

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid("Tell me a joke."))
        self.assertTrue(self.plugin.is_valid("Joke"))
        self.assertFalse(self.plugin.is_valid("What time is it?"))

    def test_handle_method(self):
        mic = testutils.TestMic(inputs=["Who's there?", "Random response"])
        jokes = joke.get_jokes()
        self.plugin.handle("Tell me a joke.", mic)
        self.assertEqual(len(mic.outputs), 3)
        self.assertIn((mic.outputs[1], mic.outputs[2]), jokes)
