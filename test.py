#!/usr/bin/env python
# -*- coding: utf-8-*-
import os
import sys
import unittest
import tempfile
from mock import patch
import cmuclmtk
import client.vocabcompiler as vocabcompiler
import client.g2p as g2p

class UnorderedList(list):
    def __eq__(self, other):
        return sorted(self) == sorted(other)
    

class TestVocabCompiler(unittest.TestCase):

    def testWordExtraction(self):
        with tempfile.NamedTemporaryFile(prefix='dictionary', suffix='.dic', delete=False) as f:
            dictionary = f.name
        with tempfile.NamedTemporaryFile(prefix='languagemodel', suffix='.lm', delete=False) as f:
            languagemodel = f.name

        
        words = ['BIRTHDAY', 'EMAIL', 'FACEBOOK', 'FIRST', 'HACKER', 'INBOX', 'JOKE', 'KNOCK',
            'LIFE', 'MEANING', 'MUSIC', 'NEWS', 'NO', 'NOTIFICATION', 'OF', 'SECOND',
            'SPOTIFY', 'THIRD', 'TIME', 'TODAY', 'TOMORROW', 'WEATHER', 'YES']

        with patch.object(g2p, 'translateWords') as translateWords:
            with patch.object(cmuclmtk, 'text2lm') as text2lm:
                text = "<s> %s </s>" % ' '.join(words)
                lm_words = vocabcompiler.create_languagemodel(text, languagemodel)
                vocabcompiler.create_dict(lm_words, dictionary)

                # 'words' is appended with ['MUSIC', 'SPOTIFY']
                # so must be > 2 to have received WORDS from modules
                translateWords.assert_called_once_with(UnorderedList(words))
                self.assertTrue(text2lm.called)
        
        os.remove(dictionary)
        os.remove(languagemodel)

if __name__ == '__main__':
    unittest.main()
