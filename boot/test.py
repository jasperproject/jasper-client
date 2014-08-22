import os

if os.environ.get('JASPER_HOME') is None:
    os.environ['JASPER_HOME'] = '/home/pi'

import sys
import unittest
from mock import patch
import vocabcompiler

lib_path = os.path.abspath('../client')
mod_path = os.path.abspath('../client/modules/')

sys.path.append(lib_path)
sys.path.append(mod_path)

import g2p


class UnorderedList(list):

    def __eq__(self, other):
        return sorted(self) == sorted(other)


class TestVocabCompiler(unittest.TestCase):

    def testWordExtraction(self):
        sentences = "temp_sentences.txt"
        dictionary = "temp_dictionary.dic"
        languagemodel = "temp_languagemodel.lm"

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

if __name__ == '__main__':
    unittest.main()
