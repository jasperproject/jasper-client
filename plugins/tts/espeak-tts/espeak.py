import logging
import pipes
import subprocess
import tempfile
from client import diagnose
from client import plugin

if not diagnose.check_executable('espeak'):
    raise ImportError("espeak executable not found!")


class EspeakTTSPlugin(plugin.TTSPlugin):
    """
    Uses the eSpeak speech synthesizer included in the Jasper disk image
    Requires espeak to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)
        try:
            voice = self.profile['espeak-tts']['voice']
        except KeyError:
            voice = 'default+m3'
        self.voice = voice

        try:
            pitch_adjustment = self.profile['espeak-tts']['pitch_adjustment']
        except KeyError:
            pitch_adjustment = 40
        self.pitch_adjustment = pitch_adjustment

        try:
            words_per_minute = self.profile['espeak-tts']['words_per_minute']
        except KeyError:
            words_per_minute = 160
        self.words_per_minute = words_per_minute

    def say(self, phrase):
        with tempfile.SpooledTemporaryFile() as out_f:
            cmd = ['espeak', '-v', self.voice,
                             '-p', self.pitch_adjustment,
                             '-s', self.words_per_minute,
                             '--stdout',
                             phrase]
            cmd = [str(x) for x in cmd]
            self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                         for arg in cmd]))
            subprocess.call(cmd, stdout=out_f)
            out_f.seek(0)
            data = out_f.read()
            return data
