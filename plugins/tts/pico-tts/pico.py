import logging
import os
import pipes
import re
import subprocess
import tempfile
from client import diagnose
from client import plugin

EXECUTABLE = 'pico2wave'

if not diagnose.check_executable(EXECUTABLE):
    raise ImportError("Executable '%s' not found!" % EXECUTABLE)


class PicoTTSPlugin(plugin.TTSPlugin):
    """
    Uses the svox-pico-tts speech synthesizer
    Requires pico2wave to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        self.language = "en-US"  # FIXME

    @property
    def languages(self):
        cmd = [EXECUTABLE, '-l', 'NULL',
                           '-w', os.devnull,
                           'NULL']
        with tempfile.SpooledTemporaryFile() as f:
            subprocess.call(cmd, stderr=f)
            f.seek(0)
            output = f.read()
        pattern = re.compile(r'Unknown language: NULL\nValid languages:\n' +
                             r'((?:[a-z]{2}-[A-Z]{2}\n)+)')
        matchobj = pattern.match(output)
        if not matchobj:
            raise RuntimeError("%s: valid languages not detected" % EXECUTABLE)
        langs = matchobj.group(1).split()
        return langs

    def say(self, phrase):
        logger = logging.getLogger(__name__)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = [EXECUTABLE, '--wave', fname]
        if self.language not in self.languages:
                raise ValueError("Language not supported")
        cmd.extend(['-l', self.language])
        cmd.append(phrase)
        logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                               for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                logger.debug("Output was: '%s'", output)
        with open(fname, 'rb') as f:
            data = f.read()
        os.remove(fname)
        return data
