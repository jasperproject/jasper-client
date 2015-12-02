import logging
import os
import pipes
import platform
import subprocess
import tempfile
from client import diagnose
from client import plugin

EXECUTABLE = 'say'

if not platform.system().lower() == 'darwin':
    raise ImportError('Invalid platform!')

if not diagnose.check_executable(EXECUTABLE):
    raise ImportError("Executable '%s' not found!" % EXECUTABLE)


class MacOSXTTSPlugin(plugin.TTSPlugin):
    """
    Uses the OS X built-in 'say' command
    """
    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self._logger.warning("This TTS plugin doesn't have multilanguage " +
                             "support!")

    def say(self, phrase):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = [EXECUTABLE, '-o', fname,
                           '--file-format=WAVE',
                           str(phrase)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.SpooledTemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)

        with open(fname, 'rb') as f:
            data = f.read()
        os.remove(fname)
        return data
