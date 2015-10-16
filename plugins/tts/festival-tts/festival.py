import logging
import pipes
import subprocess
import tempfile
from client import diagnose
from client import plugin


def check_default_voice():
    logger = logging.getLogger(__name__)
    cmd = ['festival', '--pipe']
    with tempfile.SpooledTemporaryFile() as out_f:
        with tempfile.SpooledTemporaryFile() as in_f:
            logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                   for arg in cmd]))
            subprocess.call(cmd, stdin=in_f, stdout=out_f,
                            stderr=out_f)
            out_f.seek(0)
            output = out_f.read().strip()
            if output:
                logger.debug("Output was: '%s'", output)
            return ('No default voice found' not in output)
    return False

if not all(diagnose.check_executable(e) for e in ('text2wave', 'festival')):
    raise ImportError('Executables "text2wave" and/or  "festival" not found!')

if not check_default_voice():
    raise ImportError('Festival default voice not found')


class FestivalTTSPlugin(plugin.TTSPlugin):
    """
    Uses the festival speech synthesizer
    Requires festival (text2wave) to be available
    """

    def say(self, phrase):
        logger = logging.getLogger(__name__)
        cmd = ['text2wave']
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as in_f:
                in_f.write(phrase)
                in_f.seek(0)
                with tempfile.SpooledTemporaryFile() as err_f:
                    logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                           for arg in cmd]))
                    subprocess.call(cmd, stdin=in_f, stdout=out_f,
                                    stderr=err_f)
                    err_f.seek(0)
                    output = err_f.read()
                    if output:
                        logger.debug("Output was: '%s'", output)
            out_f.seek(0)
            return out_f.read()
