#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
import tempfile
import mock
from client import g2p


def phonetisaurus_installed():
    try:
        g2p.PhonetisaurusG2P(**g2p.PhonetisaurusG2P.get_config())
    except OSError:
        return False
    else:
        return True


WORDS = ['GOOD', 'BAD', 'UGLY']


@unittest.skipUnless(phonetisaurus_installed(),
                     "Phonetisaurus or fst_model not present")
class TestG2P(unittest.TestCase):

    def setUp(self):
        self.g2pconv = g2p.PhonetisaurusG2P(
            **g2p.PhonetisaurusG2P.get_config())

    def testTranslateWord(self):
        for word in WORDS:
            self.assertIn(word, self.g2pconv.translate(word).keys())

    def testTranslateWords(self):
        results = self.g2pconv.translate(WORDS).keys()
        for word in WORDS:
            self.assertIn(word, results)


class TestPatchedG2P(unittest.TestCase):
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
        with mock.patch('client.g2p.diagnose.check_executable',
                        return_value=True):
            with tempfile.NamedTemporaryFile() as f:
                conf = g2p.PhonetisaurusG2P.get_config().items()
                with mock.patch.object(g2p.PhonetisaurusG2P, 'get_config',
                                       classmethod(lambda cls: dict(conf +
                                                   [('fst_model', f.name)]))):
                    self.g2pconv = g2p.PhonetisaurusG2P(
                        **g2p.PhonetisaurusG2P.get_config())

    def testTranslateWord(self):
            with mock.patch('subprocess.Popen',
                            return_value=TestPatchedG2P.DummyProc()):
                for word in WORDS:
                    self.assertIn(word, self.g2pconv.translate(word).keys())

    def testTranslateWords(self):
            with mock.patch('subprocess.Popen',
                            return_value=TestPatchedG2P.DummyProc()):
                results = self.g2pconv.translate(WORDS).keys()
                for word in WORDS:
                    self.assertIn(word, results)
