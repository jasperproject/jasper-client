import contextlib
import tempfile
import shutil
import mock
import unittest
from .. import sphinxvocab


@contextlib.contextmanager
def do_in_tempdir():
    tempdir = tempfile.mkdtemp()
    yield tempdir
    shutil.rmtree(tempdir)

WORDS = {'GOOD': ['G UH D', 'G UW D'],
         'BAD': ['B AE D'],
         'UGLY': ['AH G L IY']}


class DummyG2P(object):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def get_config(self, *args, **kwargs):
        return {}

    def translate(self, *args, **kwargs):
        return WORDS


def write_test_vocab(text, output_file):
    with open(output_file, "w") as f:
        for word in text.split(' '):
            f.write("%s\n" % word)


def write_test_lm(text, output_file, **kwargs):
    with open(output_file, "w") as f:
        f.write("TEST")


class TestPocketsphinxVocabulary(unittest.TestCase):
    def testVocabulary(self):
        with mock.patch.object(sphinxvocab, 'cmuclmtk',
                               create=True) as mocked_cmuclmtk:
            mocked_cmuclmtk.text2vocab = write_test_vocab
            mocked_cmuclmtk.text2lm = write_test_lm
            with mock.patch.object(sphinxvocab, 'PhonetisaurusG2P', DummyG2P):
                with tempfile.NamedTemporaryFile() as f:
                    config = {
                        'pocketsphinx': {
                            'fst_model': f.name
                        }
                    }
                    with do_in_tempdir() as tempdir:
                        sphinxvocab.compile_vocabulary(
                            config, tempdir, WORDS.keys())
