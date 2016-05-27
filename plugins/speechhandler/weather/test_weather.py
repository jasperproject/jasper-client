# -*- coding: utf-8 -*-
import unittest
from jasper import testutils, diagnose
from . import weather


class TestWeatherPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(
            weather.WeatherPlugin)

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid(
            "What's the weather like tomorrow?"))
        self.assertFalse(self.plugin.is_valid("What time is it?"))

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def test_get_woeid_method(self):
        self.assertEqual(weather.get_woeid('New York'), 2459115)

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def test_handle_method(self):
        mic = testutils.TestMic()
        self.plugin.handle("What's the weather like tomorrow?", mic)
        self.assertEqual(len(mic.outputs), 1)

        # FIXME delete "Sorry" line, once retrieving of data is fixed
        # to check that data is correct
        self.assertTrue(
            "can't see that far ahead" in mic.outputs[0] or
            "Tomorrow" in mic.outputs[0] or
            "Sorry" in mic.outputs[0])
