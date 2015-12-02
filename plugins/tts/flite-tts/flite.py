import logging
import os
import pipes
import subprocess
import tempfile
from client import diagnose
from client import plugin

EXECUTABLE = 'flite'

if not diagnose.check_executable(EXECUTABLE):
    raise ImportError("Executable '%s' not found!" % EXECUTABLE)


class FliteTTSPlugin(plugin.TTSPlugin):
    """
    Uses the flite speech synthesizer
    Requires flite to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)
        self._logger.warning("This TTS plugin doesn't have multilanguage " +
                             "support!")
        try:
            voice = self.profile['flite-tts']['voice']
        except KeyError:
            voice = ''
        else:
            if not voice or voice not in self.get_voices():
                voice = ''
        self.voice = voice

    @classmethod
    def get_voices(cls):
        cmd = ['flite', '-lv']
        voices = []
        with tempfile.SpooledTemporaryFile() as out_f:
            subprocess.call(cmd, stdout=out_f)
            out_f.seek(0)
            for line in out_f:
                if line.startswith('Voices available: '):
                    voices.extend([x.strip() for x in line[18:].split()
                                   if x.strip()])
        return voices

    def say(self, phrase):
        cmd = ['flite']
        if self.voice:
            cmd.extend(['-voice', self.voice])
        cmd.extend(['-t', phrase])
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd.append(fname)
        with tempfile.SpooledTemporaryFile() as out_f:
            self._logger.debug('Executing %s',
                               ' '.join([pipes.quote(arg)
                                         for arg in cmd]))
            subprocess.call(cmd, stdout=out_f, stderr=out_f)
            out_f.seek(0)
            output = out_f.read().strip()
        if output:
            self._logger.debug("Output was: '%s'", output)

        with open(fname, 'rb') as f:
            data = f.read()
        os.remove(fname)
        return data
