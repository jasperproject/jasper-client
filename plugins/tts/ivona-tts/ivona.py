import os
import tempfile
import pyvona
from client import plugin


class IvonaTTSPlugin(plugin.TTSPlugin):
    """
    Uses the Ivona Speech Cloud Services.
    Ivona is a multilingual Text-to-Speech synthesis platform developed by
    Amazon.
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        try:
            access_key = self.profile['ivona-tts']['access_key']
        except KeyError:
            raise ValueError("Ivona access key not configured!")

        try:
            secret_key = self.profile['ivona-tts']['secret_key']
        except KeyError:
            raise ValueError("Ivona secret key not configured!")

        try:
            region = self.profile['ivona-tts']['region']
        except KeyError:
            region = None

        try:
            voice = self.profile['ivona-tts']['voice']
        except KeyError:
            voice = None

        try:
            speech_rate = self.profile['ivona-tts']['speech_rate']
        except KeyError:
            speech_rate = None

        try:
            sentence_break = self.profile['ivona-tts']['sentence_break']
        except KeyError:
            sentence_break = None

        self._pyvonavoice = pyvona.Voice(access_key, secret_key)
        self._pyvonavoice.codec = "mp3"
        if region is not None:
            self._pyvonavoice.region = region
        if voice is not None:
            self._pyvonavoice.voice_name = voice
        if speech_rate is not None:
            self._pyvonavoice.speech_rate = speech_rate
        if sentence_break is not None:
            self._pyvonavoice.sentence_break = sentence_break

    def say(self, phrase):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        self._pyvonavoice.fetch_voice(phrase, tmpfile)
        data = self.mp3_to_wave(tmpfile)
        os.remove(tmpfile)
        return data
