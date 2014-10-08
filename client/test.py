#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import sys
import unittest
import logging
import tempfile
import shutil
import contextlib
import argparse
from mock import patch, Mock

import test_mic
import vocabcompiler
import g2p
import brain
import jasperpath
import tts
import diagnose
from stt import TranscriptionMode

DEFAULT_PROFILE = {
    'prefers_email': False,
    'location': '08544',
    'timezone': 'US/Eastern',
    'phone_number': '012344321'
}


class TestVocabCompiler(unittest.TestCase):

    def testPhraseExtraction(self):
        expected_phrases = ['MOCK']

        mock_module = Mock()
        mock_module.WORDS = ['MOCK']

        with patch.object(brain.Brain, 'get_modules',
                          classmethod(lambda cls: [mock_module])):
            extracted_phrases = vocabcompiler.get_all_phrases()
        self.assertEqual(expected_phrases, extracted_phrases)

    def testKeywordPhraseExtraction(self):
        expected_phrases = ['MOCK']

        with tempfile.TemporaryFile() as f:
            # We can't use mock_open here, because it doesn't seem to work
            # with the 'for line in f' syntax
            f.write("MOCK\n")
            f.seek(0)
            with patch('%s.open' % vocabcompiler.__name__,
                       return_value=f, create=True):
                extracted_phrases = vocabcompiler.get_keyword_phrases()
        self.assertEqual(expected_phrases, extracted_phrases)


class TestVocabulary(unittest.TestCase):
    VOCABULARY = vocabcompiler.DummyVocabulary

    @contextlib.contextmanager
    def do_in_tempdir(self):
        tempdir = tempfile.mkdtemp()
        yield tempdir
        shutil.rmtree(tempdir)

    def testVocabulary(self):
        phrases = ['GOOD BAD UGLY']
        with self.do_in_tempdir() as tempdir:
            self.vocab = self.VOCABULARY(path=tempdir)
            self.assertIsNone(self.vocab.compiled_revision)
            self.assertFalse(self.vocab.is_compiled)
            self.assertFalse(self.vocab.matches_phrases(phrases))

            # We're now testing error handling. To avoid flooding the
            # output with error messages that are catched anyway,
            # we'll temporarly disable logging. Otherwise, error log
            # messages and traceback would be printed so that someone
            # might think that tests failed even though they succeeded.
            logging.disable(logging.ERROR)
            with self.assertRaises(OSError):
                with patch('os.makedirs', side_effect=OSError('test')):
                    self.vocab.compile(phrases)
            with self.assertRaises(OSError):
                with patch('%s.open' % vocabcompiler.__name__,
                           create=True,
                           side_effect=OSError('test')):
                    self.vocab.compile(phrases)

            class StrangeCompilationError(Exception):
                pass
            with patch.object(self.vocab, '_compile_vocabulary',
                              side_effect=StrangeCompilationError('test')):
                with self.assertRaises(StrangeCompilationError):
                    self.vocab.compile(phrases)
                with self.assertRaises(StrangeCompilationError):
                    with patch('os.remove',
                               side_effect=OSError('test')):
                        self.vocab.compile(phrases)
            # Re-enable logging again
            logging.disable(logging.NOTSET)

            self.vocab.compile(phrases)
            self.assertIsInstance(self.vocab.compiled_revision, str)
            self.assertTrue(self.vocab.is_compiled)
            self.assertTrue(self.vocab.matches_phrases(phrases))
            self.vocab.compile(phrases)
            self.vocab.compile(phrases, force=True)


class TestPocketsphinxVocabulary(TestVocabulary):

    VOCABULARY = vocabcompiler.PocketsphinxVocabulary

    def testVocabulary(self):
        super(TestPocketsphinxVocabulary, self).testVocabulary()
        self.assertIsInstance(self.vocab.decoder_kwargs, dict)
        self.assertIn('lm', self.vocab.decoder_kwargs)
        self.assertIn('dict', self.vocab.decoder_kwargs)


class TestPatchedPocketsphinxVocabulary(TestPocketsphinxVocabulary):

    def testVocabulary(self):

        def write_test_vocab(text, output_file):
            with open(output_file, "w") as f:
                for word in text.split(' '):
                    f.write("%s\n" % word)

        def write_test_lm(text, output_file, **kwargs):
            with open(output_file, "w") as f:
                f.write("TEST")

        class DummyG2P(object):
            def __init__(self, *args, **kwargs):
                pass

            @classmethod
            def get_config(self, *args, **kwargs):
                return {}

            def translate(self, *args, **kwargs):
                return {'GOOD': ['G UH D',
                                 'G UW D'],
                        'BAD': ['B AE D'],
                        'UGLY': ['AH G L IY']}

        with patch('vocabcompiler.cmuclmtk',
                   create=True) as mocked_cmuclmtk:
            mocked_cmuclmtk.text2vocab = write_test_vocab
            mocked_cmuclmtk.text2lm = write_test_lm
            with patch('vocabcompiler.PhonetisaurusG2P', DummyG2P):
                super(TestPatchedPocketsphinxVocabulary,
                      self).testVocabulary()


class TestMic(unittest.TestCase):

    def setUp(self):
        self.jasper_clip = jasperpath.data('audio', 'jasper.wav')
        self.time_clip = jasperpath.data('audio', 'time.wav')

        from stt import PocketSphinxSTT
        self.stt = PocketSphinxSTT(**PocketSphinxSTT.get_config())

    def testTranscribeJasper(self):
        """
        Does Jasper recognize his name (i.e., passive listen)?
        """
        with open(self.jasper_clip, mode="rb") as f:
            transcription = self.stt.transcribe(f,
                                                mode=TranscriptionMode.KEYWORD)
        self.assertIn("JASPER", transcription)

    def testTranscribe(self):
        """
        Does Jasper recognize 'time' (i.e., active listen)?
        """
        with open(self.time_clip, mode="rb") as f:
            transcription = self.stt.transcribe(f)
        self.assertIn("TIME", transcription)


class TestG2P(unittest.TestCase):

    def setUp(self):
        self.g2pconverter = g2p.PhonetisaurusG2P(
            **g2p.PhonetisaurusG2P.get_config())
        self.words = ['GOOD', 'BAD', 'UGLY']

    def testTranslateWord(self):
        for word in self.words:
            self.assertIn(word, self.g2pconverter.translate(word).keys())

    def testTranslateWords(self):
        results = self.g2pconverter.translate(self.words).keys()
        for word in self.words:
            self.assertIn(word, results)


class TestPatchedG2P(TestG2P):
    class DummyProc(object):
        def __init__(self, *args, **kwargs):
            self.returncode = 0

        def communicate(self):
            return ("GOOD\t9.20477\t<s> G UH D </s>\n" +
                    "GOOD\t14.4036\t<s> G UW D </s>\n" +
                    "GOOD\t16.0258\t<s> G UH D IY </s>\n" +
                    "BAD\t0.7416\t<s> B AE D </s>\n" +
                    "BAD\t12.5495\t<s> B AA D </s>\n" +
                    "BAD\t13.6745\t<s> B AH D </s>\n" +
                    "UGLY\t12.572\t<s> AH G L IY </s>\n" +
                    "UGLY\t17.9278\t<s> Y UW G L IY </s>\n" +
                    "UGLY\t18.9617\t<s> AH G L AY </s>\n", "")

    def setUp(self):
        with patch('g2p.diagnose.check_executable',
                   return_value=True):
            with tempfile.NamedTemporaryFile() as f:
                conf = g2p.PhonetisaurusG2P.get_config().items()
                with patch.object(g2p.PhonetisaurusG2P, 'get_config',
                                  classmethod(lambda cls: dict(
                                      conf + [('fst_model', f.name)]))):
                    super(self.__class__, self).setUp()

    def testTranslateWord(self):
            with patch('subprocess.Popen',
                       return_value=TestPatchedG2P.DummyProc()):
                super(self.__class__, self).testTranslateWord()

    def testTranslateWords(self):
            with patch('subprocess.Popen',
                       return_value=TestPatchedG2P.DummyProc()):
                super(self.__class__, self).testTranslateWords()


class TestDiagnose(unittest.TestCase):
    def testPythonImportCheck(self):
        # This a python stdlib module that definitely exists
        self.assertTrue(diagnose.check_python_import("os"))
        # I sincerly hope nobody will ever create a package with that name
        self.assertFalse(diagnose.check_python_import("nonexistant_package"))


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
        allJokes = open(jasperpath.data('text', 'JOKES.txt'), 'r').read()
        self.assertTrue(outputs[2] in allJokes)

    def testTime(self):
        from modules import Time

        query = "What time is it?"
        inputs = []
        self.runConversation(query, inputs, Time)

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testGmail(self):
        key = 'gmail_password'
        if key not in self.profile or not self.profile[key]:
            return

        from modules import Gmail

        query = "Check my email"
        inputs = []
        self.runConversation(query, inputs, Gmail)

    @unittest.skipIf(not diagnose.check_network_connection(),
                     "No internet connection")
    def testHN(self):
        from modules import HN

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
        from modules import News

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
        from modules import Weather

        query = "what's the weather like tomorrow"
        inputs = []
        outputs = self.runConversation(query, inputs, Weather)
        self.assertTrue(
            "can't see that far ahead" in outputs[0]
            or "Tomorrow" in outputs[0])


class TestTTS(unittest.TestCase):
    def testTTS(self):
        tts_engine = tts.get_engine_by_slug('dummy-tts')
        tts_instance = tts_engine()
        tts_instance.say('This is a test.')


class TestBrain(unittest.TestCase):

    @staticmethod
    def _emptyBrain():
        mic = test_mic.Mic([])
        profile = DEFAULT_PROFILE
        return brain.Brain(mic, profile)

    def testLog(self):
        """Does Brain correctly log errors when raised by modules?"""
        my_brain = TestBrain._emptyBrain()
        unclear = my_brain.modules[-1]
        with patch.object(unclear, 'handle') as mocked_handle:
            with patch.object(my_brain._logger, 'error') as mocked_loggingcall:
                mocked_handle.side_effect = KeyError('foo')
                my_brain.query("zzz gibberish zzz")
                self.assertTrue(mocked_loggingcall.called)

    def testSortByPriority(self):
        """Does Brain sort modules by priority?"""
        my_brain = TestBrain._emptyBrain()
        priorities = filter(lambda m: hasattr(m, 'PRIORITY'), my_brain.modules)
        target = sorted(priorities, key=lambda m: m.PRIORITY, reverse=True)
        self.assertEqual(target, priorities)

    def testPriority(self):
        """Does Brain correctly send query to higher-priority module?"""
        my_brain = TestBrain._emptyBrain()
        hn_module = 'HN'
        hn = filter(lambda m: m.__name__ == hn_module, my_brain.modules)[0]

        with patch.object(hn, 'handle') as mocked_handle:
            my_brain.query(["hacker news"])
            self.assertTrue(mocked_handle.called)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test suite for the Jasper client code.')
    parser.add_argument('--light', action='store_true',
                        help='runs a subset of the tests (only requires ' +
                             'Python dependencies)')
    parser.add_argument('--debug', action='store_true',
                        help='show debug messages')
    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Change CWD to jasperpath.LIB_PATH
    os.chdir(jasperpath.LIB_PATH)

    test_cases = [TestBrain, TestModules, TestDiagnose, TestTTS,
                  TestVocabCompiler, TestVocabulary]
    if args.light:
        test_cases.append(TestPatchedG2P)
        test_cases.append(TestPatchedPocketsphinxVocabulary)
    else:
        test_cases.append(TestG2P)
        test_cases.append(TestPocketsphinxVocabulary)
        test_cases.append(TestMic)

    suite = unittest.TestSuite()

    for test_case in test_cases:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_case))

    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        sys.exit("Tests failed")
