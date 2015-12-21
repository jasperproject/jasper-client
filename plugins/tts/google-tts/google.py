import os
import tempfile
import gtts
from client import plugin


class GoogleTTSPlugin(plugin.TTSPlugin):
    """
    Uses the Google TTS online translator
    Requires pymad and gTTS to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)
        try:
            orig_language = self.profile['language']
        except:
            orig_language = 'en-US'

        language = orig_language.lower()

        if language not in gtts.gTTS.LANGUAGES:
            language = language.split('-')[0]

        if language not in gtts.gTTS.LANGUAGES:
            raise ValueError("Language '%s' ('%s') not supported" %
                             (language, orig_language))

        self.language = language

    def say(self, phrase):

        tts = gtts.gTTS(text=phrase, lang=self.language)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        data = self.mp3_to_wave(tmpfile)
        os.remove(tmpfile)
        return data
