import logging
import re
import subprocess
import tempfile
from client import diagnose
from client import plugin
from . import juliusvocab

if not diagnose.check_executable('julius'):
    raise ImportError("Can't find julius executable")


RE_SENTENCE = re.compile(r'sentence(\d+): <s> (.+) </s>')


class JuliusSTTPlugin(plugin.STTPlugin):
    """
    A very basic Speech-to-Text engine using Julius.
    """
    def __init__(self, *args, **kwargs):
        plugin.STTPlugin.__init__(self, *args, **kwargs)
        self._logger = logging.getLogger(__name__)

        self._logger.warning("This STT plugin doesn't have multilanguage " +
                             "support!")

        vocabulary_path = self.compile_vocabulary(
          juliusvocab.compile_vocabulary)

        self._dfa_file = juliusvocab.get_dfa_path(vocabulary_path)
        self._dict_file = juliusvocab.get_dict_path(vocabulary_path)

        try:
            hmmdefs = self.profile['julius']['hmmdefs']
        except KeyError:
            hmmdefs = "/usr/share/voxforge/julius/acoustic_model_files/hmmdefs"

        try:
            tiedlist = self.profile['julius']['tiedlist']
        except KeyError:
            tiedlist = "/usr/share/voxforge/julius/acoustic_model_files/" + \
                       "tiedlist"

        self._hmmdefs = hmmdefs
        self._tiedlist = tiedlist

        # Inital test run: we run this command once to log errors/warnings
        cmd = ['julius',
               '-input', 'stdin',
               '-dfa', self._dfa_file,
               '-v', self._dict_file,
               '-h', self._hmmdefs,
               '-hlist', self._tiedlist,
               '-forcedict']
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing: %r', cmd)
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as f:
                with tempfile.SpooledTemporaryFile() as err_f:
                    subprocess.call(cmd, stdin=f, stdout=out_f, stderr=err_f)
            out_f.seek(0)
            for line in out_f.read().splitlines():
                line = line.strip()
                if len(line) > 7 and line[:7].upper() == 'ERROR: ':
                    if not line[7:].startswith('adin_'):
                        self._logger.error(line[7:])
                elif len(line) > 9 and line[:9].upper() == 'WARNING: ':
                    self._logger.warning(line[9:])
                elif len(line) > 6 and line[:6].upper() == 'STAT: ':
                    self._logger.debug(line[6:])

    def transcribe(self, fp, mode=None):
        cmd = ['julius',
               '-quiet',
               '-nolog',
               '-input', 'stdin',
               '-dfa', self._vocabulary.dfa_file,
               '-v', self._vocabulary.dict_file,
               '-h', self._hmmdefs,
               '-hlist', self._tiedlist,
               '-forcedict']
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing: %r', cmd)
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as err_f:
                subprocess.call(cmd, stdin=fp, stdout=out_f, stderr=err_f)
            out_f.seek(0)
            results = [(int(i), text) for i, text in
                       RE_SENTENCE.findall(out_f.read())]
        transcribed = [text for i, text in
                       sorted(results, key=lambda x: x[0])
                       if text]
        if not transcribed:
            transcribed.append('')
        self._logger.info('Transcribed: %r', transcribed)
        return transcribed

    def get_vocabulary_type(self):
        return JuliusVocabulary
