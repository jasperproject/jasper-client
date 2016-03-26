# -*- coding: utf-8 -*-
import unittest
import os.path
from jasper import testutils, diagnose
from . import weather


class TestGmailPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(
            os.path.dirname(weather.__file__),
            extra_config={
                'Plugin weather': {
                    'location': 'New York',
                    'unit': 'f'
                }
            })

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid(
            "What's the weather like tomorrow?"))
        self.assertFalse(self.plugin.is_valid("What time is it?"))

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def test_handle_method(self):
        mic = testutils.TestMic()
        self.plugin.handle("What's the weather like tomorrow?", mic)
        self.assertEqual(len(mic.outputs), 1)
        self.assertTrue(
            "can't see that far ahead" in mic.outputs[0] or
            "Tomorrow" in mic.outputs[0])
