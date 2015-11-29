# -*- coding: utf-8 -*-
import unittest
import mock
from .. import g2p


WORDS = ['GOOD', 'BAD', 'UGLY']


class DummyProc(object):
    def __init__(self, *args, **kwargs):
        self.returncode = 0
        self.stderr = mock.Mock()
        self.stderr.readline = mock.Mock(return_value='')

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

    def poll(self):
        return 1


class TestPatchedG2P(unittest.TestCase):
    def setUp(self):
        self.g2pconv = g2p.PhonetisaurusG2P('dummy_proc', 'dummy_fst_model',
                                            nbest=3)

    def testTranslateWord(self):
        with mock.patch('subprocess.Popen',
                        return_value=DummyProc()):
            for word in WORDS:
                self.assertIn(word, self.g2pconv.translate(word).keys())

    def testTranslateWords(self):
        with mock.patch('subprocess.Popen',
                        return_value=DummyProc()):
            results = self.g2pconv.translate(WORDS).keys()
            for word in WORDS:
                self.assertIn(word, results)
