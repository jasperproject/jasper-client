#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
import tempfile
import contextlib
import logging
import shutil
import mock
from client import vocabcompiler


class TestVocabCompiler(unittest.TestCase):

    def testPhraseExtraction(self):
        expected_phrases = ['MOCK']

        mock_module = mock.Mock()
        mock_module.WORDS = ['MOCK']

        with mock.patch('client.brain.Brain.get_modules',
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
            with mock.patch('%s.open' % vocabcompiler.__name__,
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
                with mock.patch('os.makedirs', side_effect=OSError('test')):
                    self.vocab.compile(phrases)
            with self.assertRaises(OSError):
                with mock.patch('%s.open' % vocabcompiler.__name__,
                                create=True,
                                side_effect=OSError('test')):
                    self.vocab.compile(phrases)

            class StrangeCompilationError(Exception):
                pass
            with mock.patch.object(self.vocab, '_compile_vocabulary',
                                   side_effect=StrangeCompilationError('test')
                                   ):
                with self.assertRaises(StrangeCompilationError):
                    self.vocab.compile(phrases)
                with self.assertRaises(StrangeCompilationError):
                    with mock.patch('os.remove',
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

    @unittest.skipUnless(hasattr(vocabcompiler, 'cmuclmtk'),
                         "CMUCLMTK not present")
    def testVocabulary(self):
        super(TestPocketsphinxVocabulary, self).testVocabulary()
        self.assertIsInstance(self.vocab.decoder_kwargs, dict)
        self.assertIn('lm', self.vocab.decoder_kwargs)
        self.assertIn('dict', self.vocab.decoder_kwargs)

    def testPatchedVocabulary(self):

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

        with mock.patch('client.vocabcompiler.cmuclmtk',
                        create=True) as mocked_cmuclmtk:
            mocked_cmuclmtk.text2vocab = write_test_vocab
            mocked_cmuclmtk.text2lm = write_test_lm
            with mock.patch('client.vocabcompiler.PhonetisaurusG2P', DummyG2P):
                self.testVocabulary()
