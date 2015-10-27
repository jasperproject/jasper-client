# -*- coding: utf-8-*-
import unittest
from client import testutils
from . import clock


class TestClockPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(clock.ClockPlugin)

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid("What time is it?"))
        self.assertTrue(self.plugin.is_valid("Time"))
        self.assertFalse(self.plugin.is_valid("Tell me a joke."))

    def test_handle_method(self):
        mic = testutils.TestMic()
        self.plugin.handle("What time is it?", mic)
        self.assertEqual(len(mic.outputs), 1)
        self.assertIn("It is", mic.outputs[0])
