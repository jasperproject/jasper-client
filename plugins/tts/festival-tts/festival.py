import logging
import pipes
import subprocess
import tempfile
from client import diagnose
from client import plugin


if not all(diagnose.check_executable(e) for e in ('text2wave', 'festival')):
    raise ImportError('Executables "text2wave" and/or  "festival" not found!')


class FestivalTTSPlugin(plugin.TTSPlugin):
    """
    Uses the festival speech synthesizer
    Requires festival (text2wave) to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)

        available_voices = self.get_voices()
        if len(available_voices) == 0:
            raise ValueError('No voices available!')

        self._logger.warning("This TTS plugin doesn't have multilanguage " +
                             "support!")
        self._logger.info('Available voices: %s', ', '.join(available_voices))

        try:
            voice = self.profile['festival-tts']['voice']
        except KeyError:
            voice = None

        if voice is None or voice not in available_voices:
            if voice is not None:
                self._logger.warning("Voice '%s' not available!", voice)
            default_voice = self.get_default_voice()
            if default_voice in available_voices:
                self.voice = default_voice
            else:
                self.voice = available_voices[0]
        self._logger.info("Using voice '%s'.", self.voice)

    def execute_scheme_command(self, command):
        cmd = ['festival', '--pipe']
        self._logger.debug("Executing festival command '%s'", command)
        with tempfile.SpooledTemporaryFile() as in_f:
            in_f.write(command)
            in_f.seek(0)
            with tempfile.SpooledTemporaryFile() as out_f:
                subprocess.call(cmd, stdin=in_f, stdout=out_f)
                out_f.seek(0)
                output = out_f.read().strip()
        self._logger.debug("Festival command output '%s'",
                           output.replace('\n', '\\n'))
        return output

    def get_voices(self):
        output = self.execute_scheme_command(
            '(mapcar (lambda (v) (print v)) (voice.list))')
        return [l for l in output.splitlines() if l.strip() != '']

    def get_default_voice(self):
        output = self.execute_scheme_command('(print voice_default)')
        if output == 0:
            return None
        return output[len('voice_'):]

    def say(self, phrase):
        cmd = ['text2wave', '-eval', '(voice_%s)' % self.voice]
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as in_f:
                in_f.write(phrase)
                in_f.seek(0)
                with tempfile.SpooledTemporaryFile() as err_f:
                    self._logger.debug(
                        'Executing %s', ' '.join([pipes.quote(arg)
                                                  for arg in cmd]))
                    subprocess.call(cmd, stdin=in_f, stdout=out_f,
                                    stderr=err_f)
                    err_f.seek(0)
                    output = err_f.read()
                    if output:
                        self._logger.debug("Output was: '%s'", output)
            out_f.seek(0)
            return out_f.read()
