#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import unittest
import tempfile
import contextlib
import logging
import shutil
import mock
from client import vocabcompiler


class StrangeCompilationError(Exception):
    pass


def nop_func(*args):
    pass


def error_func(*args):
    raise StrangeCompilationError('This is a test.')


class TestVocabulary(unittest.TestCase):
    @contextlib.contextmanager
    def do_in_tempdir(self):
        tempdir = tempfile.mkdtemp()
        yield tempdir
        shutil.rmtree(tempdir)

    def testVocabulary(self):
        phrases = ['GOOD BAD UGLY']
        with self.do_in_tempdir() as tempdir:
            self.vocab = vocabcompiler.VocabularyCompiler(
                "unittest", path=tempdir)
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
                    self.vocab.compile(None, nop_func, phrases)
            with self.assertRaises(OSError):
                with mock.patch('%s.open' % vocabcompiler.__name__,
                                create=True,
                                side_effect=OSError('test')):
                    self.vocab.compile(None, nop_func, phrases)

                with self.assertRaises(StrangeCompilationError):
                    self.vocab.compile(None, error_func, phrases)

                with self.assertRaises(StrangeCompilationError):
                    with mock.patch('os.remove',
                                    side_effect=OSError('test')):
                        self.vocab.compile(None, error_func, phrases)

            # Re-enable logging again
            logging.disable(logging.NOTSET)

            self.vocab.compile(None, nop_func, phrases)
            self.assertIsInstance(self.vocab.compiled_revision, str)
            self.assertTrue(self.vocab.is_compiled)
            self.assertTrue(self.vocab.matches_phrases(phrases))
            self.vocab.compile(None, nop_func, phrases)
            self.vocab.compile(None, nop_func, phrases, force=True)
