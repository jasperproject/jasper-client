#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
from client import test_mic, diagnose, jasperpath
from client.modules import Life, Joke, Time, Gmail, HN, News, Weather

DEFAULT_PROFILE = {
    'prefers_email': False,
    'location': 'Cape Town',
    'timezone': 'US/Eastern',
    'phone_number': '012344321'
}


class TestModules(unittest.TestCase):

    def setUp(self):
        self.profile = DEFAULT_PROFILE
        self.send = False

    def runConversation(self, query, inputs, module):
        """Generic method for spoofing conversation.

        Arguments:
        query -- The initial input to the server.
        inputs -- Additional input, if conversation is extended.

        Returns:
        The server's responses, in a list.
        """
        self.assertTrue(module.is_valid(query))
        mic = test_mic.Mic(inputs)
        module.handle(query, mic, self.profile)
        return mic.outputs

    def testLife(self):
        query = "What is the meaning of life?"
        inputs = []
        outputs = self.runConversation(query, inputs, Life)
        self.assertEqual(len(outputs), 1)
        self.assertTrue("42" in outputs[0])

    def testJoke(self):
        query = "Tell me a joke."
        inputs = ["Who's there?", "Random response"]
        outputs = self.runConversation(query, inputs, Joke)
        self.assertEqual(len(outputs), 3)
        allJokes = open(jasperpath.data('text', 'JOKES.txt'), 'r').read()
        self.assertTrue(outputs[2] in allJokes)

    def testTime(self):
        query = "What time is it?"
        inputs = []
        self.runConversation(query, inputs, Time)

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testGmail(self):
        key = 'gmail_password'
        if key not in self.profile or not self.profile[key]:
            return

        query = "Check my email"
        inputs = []
        self.runConversation(query, inputs, Gmail)

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testHN(self):
        query = "find me some of the top hacker news stories"
        if self.send:
            inputs = ["the first and third"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, HN)
        self.assertTrue("front-page articles" in outputs[1])

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testNews(self):
        query = "find me some of the top news stories"
        if self.send:
            inputs = ["the first"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, News)
        self.assertTrue("top headlines" in outputs[1])

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testWeather(self):
        query = "what's the weather like tomorrow"
        inputs = []
        outputs = self.runConversation(query, inputs, Weather)
        self.assertTrue("can't see that far ahead"
                        in outputs[0] or "Tomorrow" in outputs[0])
