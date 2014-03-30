import unittest
from urllib2 import URLError, urlopen
import yaml
from test_mic import Mic
from modules import *


def activeInternet():
    try:
        urlopen('http://www.google.com', timeout=1)
        return True
    except URLError:
        return False


class TestModules(unittest.TestCase):

    def setUp(self):
        self.profile = yaml.safe_load(open("profile.yml", "r"))
        self.send = False

    def runConversation(self, query, inputs, module):
        """Generic method for spoofing conversation.

        Arguments:
        query -- The initial input to the server.
        inputs -- Additional input, if conversation is extended.

        Returns:
        The server's responses, in a list.
        """
        self.assertTrue(module.isValid(query))
        mic = Mic(inputs)
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
        allJokes = open("JOKES.txt", "r").read()
        self.assertTrue(outputs[2] in allJokes)

    def testTime(self):
        query = "What time is it?"
        inputs = []
        self.runConversation(query, inputs, Time)

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testGmail(self):
        key = 'gmail_password'
        if not key in self.profile or not self.profile[key]:
            return

        query = "Check my email"
        inputs = []
        self.runConversation(query, inputs, Gmail)

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testHN(self):
        query = "find me some of the top hacker news stories"
        if self.send:
            inputs = ["the first and third"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, HN)
        self.assertTrue("front-page articles" in outputs[1])

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testNews(self):
        query = "find me some of the top news stories"
        if self.send:
            inputs = ["the first"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, News)
        self.assertTrue("top headlines" in outputs[1])

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testWeather(self):
        query = "what's the weather like tomorrow"
        inputs = []
        outputs = self.runConversation(query, inputs, Weather)
        self.assertTrue(
            "can't see that far ahead" in outputs[0]
            or "Tomorrow" in outputs[0])


if __name__ == '__main__':
    unittest.main()
