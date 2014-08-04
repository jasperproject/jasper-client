import os
import sys
import unittest
import tempfile
from mock import patch
import client.vocabcompiler as vocabcompiler
import client.g2p as g2p

class UnorderedList(list):
    def __eq__(self, other):
        return sorted(self) == sorted(other)
    

class TestVocabCompiler(unittest.TestCase):

    def testWordExtraction(self):
        with tempfile.NamedTemporaryFile(prefix='sentences', suffix='.txt', delete=False) as f:
            sentences = f.name
        with tempfile.NamedTemporaryFile(prefix='dictionary', suffix='.dic', delete=False) as f:
            dictionary = f.name
        with tempfile.NamedTemporaryFile(prefix='languagemodel', suffix='.lm', delete=False) as f:
            languagemodel = f.name

        words = [
            'HACKER', 'LIFE', 'FACEBOOK', 'THIRD', 'NO', 'JOKE',
            'NOTIFICATION', 'MEANING', 'TIME', 'TODAY', 'SECOND',
            'BIRTHDAY', 'KNOCK KNOCK', 'INBOX', 'OF', 'NEWS', 'YES',
            'TOMORROW', 'EMAIL', 'WEATHER', 'FIRST', 'MUSIC', 'SPOTIFY'
        ]

        with patch.object(g2p, 'translateWords') as translateWords:
            with patch.object(vocabcompiler, 'text2lm') as text2lm:
                vocabcompiler.compile(sentences, dictionary, languagemodel)

                # 'words' is appended with ['MUSIC', 'SPOTIFY']
                # so must be > 2 to have received WORDS from modules
                translateWords.assert_called_once_with(UnorderedList(words))
                self.assertTrue(text2lm.called)
        
        os.remove(sentences)
        os.remove(dictionary)
        os.remove(languagemodel)

if __name__ == '__main__':
    unittest.main()
