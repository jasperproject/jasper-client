# -*- coding: utf-8 -*-
import unittest
from jasper import testutils
from .life import MeaningOfLifePlugin


class TestMeaningOfLifePlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(MeaningOfLifePlugin)

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid("What is the meaning of life?"))
        self.assertFalse(self.plugin.is_valid("What is the meaning of death?"))
        self.assertFalse(self.plugin.is_valid("What time is it?"))

    def test_handle_method(self):
        mic = testutils.TestMic()
        self.plugin.handle("What is the meaning of life?", mic)
        self.assertEqual(len(mic.outputs), 1)
        self.assertIn("42", mic.outputs[0])
