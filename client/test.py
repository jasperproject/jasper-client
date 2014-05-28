import unittest
import argparse
from mock import patch
from urllib2 import URLError, urlopen
import yaml
import test_mic
import g2p
import brain


def activeInternet():
    try:
        urlopen('http://www.google.com', timeout=1)
        return True
    except URLError:
        return False


class TestMic(unittest.TestCase):

    def setUp(self):
        self.jasper_clip = "../static/audio/jasper.wav"
        self.time_clip = "../static/audio/time.wav"

        from mic import Mic
        self.m = Mic("languagemodel.lm", "dictionary.dic",
                     "languagemodel_persona.lm", "dictionary_persona.dic")

    def testTranscribeJasper(self):
        """Does Jasper recognize his name (i.e., passive listen)?"""
        transcription = self.m.transcribe(self.jasper_clip, PERSONA_ONLY=True)
        self.assertTrue("JASPER" in transcription)

    def testTranscribe(self):
        """Does Jasper recognize 'time' (i.e., active listen)?"""
        transcription = self.m.transcribe(self.time_clip)
        self.assertTrue("TIME" in transcription)


class TestG2P(unittest.TestCase):

    def setUp(self):
        self.translations = {
            'GOOD': 'G UH D',
            'BAD': 'B AE D',
            'UGLY': 'AH G L IY'
        }

    def testTranslateWord(self):
        for word in self.translations:
            translation = self.translations[word]
            self.assertEqual(g2p.translateWord(word), translation)

    def testTranslateWords(self):
        words = self.translations.keys()
        # preserve ordering
        translations = [self.translations[w] for w in words]
        self.assertEqual(g2p.translateWords(words), translations)


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
        mic = test_mic.Mic(inputs)
        module.handle(query, mic, self.profile)
        return mic.outputs

    def testLife(self):
        from modules import Life

        query = "What is the meaning of life?"
        inputs = []
        outputs = self.runConversation(query, inputs, Life)
        self.assertEqual(len(outputs), 1)
        self.assertTrue("42" in outputs[0])

    def testJoke(self):
        from modules import Joke

        query = "Tell me a joke."
        inputs = ["Who's there?", "Random response"]
        outputs = self.runConversation(query, inputs, Joke)
        self.assertEqual(len(outputs), 3)
        allJokes = open("../static/text/JOKES.txt", "r").read()
        self.assertTrue(outputs[2] in allJokes)

    def testTime(self):
        from modules import Time

        query = "What time is it?"
        inputs = []
        self.runConversation(query, inputs, Time)

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testGmail(self):
        key = 'gmail_password'
        if not key in self.profile or not self.profile[key]:
            return

        from modules import Gmail

        query = "Check my email"
        inputs = []
        self.runConversation(query, inputs, Gmail)

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testHN(self):
        from modules import HN

        query = "find me some of the top hacker news stories"
        if self.send:
            inputs = ["the first and third"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, HN)
        self.assertTrue("front-page articles" in outputs[1])

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testNews(self):
        from modules import News

        query = "find me some of the top news stories"
        if self.send:
            inputs = ["the first"]
        else:
            inputs = ["no"]
        outputs = self.runConversation(query, inputs, News)
        self.assertTrue("top headlines" in outputs[1])

    @unittest.skipIf(not activeInternet(), "No internet connection")
    def testWeather(self):
        from modules import Weather

        query = "what's the weather like tomorrow"
        inputs = []
        outputs = self.runConversation(query, inputs, Weather)
        self.assertTrue(
            "can't see that far ahead" in outputs[0]
            or "Tomorrow" in outputs[0])


class TestBrain(unittest.TestCase):

    @staticmethod
    def _emptyBrain():
        mic = test_mic.Mic([])
        profile = yaml.safe_load(open("profile.yml", "r"))
        return brain.Brain(mic, profile)

    @patch.object(brain, 'logError')
    def testLog(self, logError):
        """Does Brain correctly log errors when raised by modules?"""
        my_brain = TestBrain._emptyBrain()
        unclear = my_brain.modules[-1]
        with patch.object(unclear, 'handle') as mocked_handle:
            mocked_handle.side_effect = KeyError('foo')
            my_brain.query("zzz gibberish zzz")
            logError.assert_called_with()

    def testSortByPriority(self):
        """Does Brain sort modules by priority?"""
        my_brain = TestBrain._emptyBrain()
        priorities = filter(lambda m: hasattr(m, 'PRIORITY'), my_brain.modules)
        target = sorted(priorities, key=lambda m: m.PRIORITY, reverse=True)
        self.assertEqual(target, priorities)

    def testPriority(self):
        """Does Brain correctly send query to higher-priority module?"""
        my_brain = TestBrain._emptyBrain()
        hn_module = 'modules.HN'
        hn = filter(lambda m: m.__name__ == hn_module, my_brain.modules)[0]

        with patch.object(hn, 'handle') as mocked_handle:
            my_brain.query("hacker news")
            self.assertTrue(mocked_handle.called)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test suite for the Jasper client code.')
    parser.add_argument('--light', action='store_true',
                        help="runs a subset of the tests (only requires Python dependencies)")
    args = parser.parse_args()

    test_cases = [TestBrain, TestModules]
    if not args.light:
        test_cases.append(TestG2P)
        test_cases.append(TestMic)

    for test_case in test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
