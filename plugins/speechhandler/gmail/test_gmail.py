# -*- coding: utf-8 -*-
import unittest
from jasper import testutils, diagnose
from . import gmail


class TestGmailPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(gmail.GmailPlugin)

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid("Do I have new email?"))
        self.assertTrue(self.plugin.is_valid("Check my email account!"))
        self.assertFalse(self.plugin.is_valid("What time is it?"))

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def test_handle_method(self):
        key = 'gmail_password'
        if key not in self.plugin.profile or not self.plugin.profile[key]:
            self.skipTest("Gmail password not available")

        mic = testutils.TestMic()
        self.plugin.handle("Check my email account!", mic)
