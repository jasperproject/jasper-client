# -*- coding: utf-8 -*-
import abc
import tempfile
import wave
import mad
from . import paths
from . import vocabcompiler
from . import audioengine
from . import i18n


class GenericPlugin(object):
    def __init__(self, info, config):
        self._plugin_config = config
        self._plugin_info = info

    @property
    def profile(self):
        # FIXME: Remove this in favor of something better
        return self._plugin_config

    @property
    def info(self):
        return self._plugin_info


class AudioEnginePlugin(GenericPlugin, audioengine.AudioEngine):
    pass


class SpeechHandlerPlugin(GenericPlugin, i18n.GettextMixin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        GenericPlugin.__init__(self, *args, **kwargs)
        i18n.GettextMixin.__init__(
            self, self.info.translations, self.profile)

    @abc.abstractmethod
    def get_phrases(self):
        pass

    @abc.abstractmethod
    def handle(self, text, mic):
        pass

    @abc.abstractmethod
    def is_valid(self, text):
        pass

    def get_priority(self):
        return 0


class STTPlugin(GenericPlugin):
    def __init__(self, name, phrases, *args, **kwargs):
        GenericPlugin.__init__(self, *args, **kwargs)
        self._vocabulary_phrases = phrases
        self._vocabulary_name = name
        self._vocabulary_compiled = False
        self._vocabulary_path = None

    def compile_vocabulary(self, compilation_func):
        if self._vocabulary_compiled:
            raise RuntimeError("Vocabulary has already been compiled!")

        try:
            language = self.profile['language']
        except KeyError:
            language = None
        if not language:
            language = 'en-US'

        vocabulary = vocabcompiler.VocabularyCompiler(
            self.info.name, self._vocabulary_name,
            path=paths.config('vocabularies', language))

        if not vocabulary.matches_phrases(self._vocabulary_phrases):
            vocabulary.compile(
                self.profile, compilation_func, self._vocabulary_phrases)

        self._vocabulary_path = vocabulary.path
        return self._vocabulary_path

    @property
    def vocabulary_path(self):
        return self._vocabulary_path

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        return True

    @abc.abstractmethod
    def transcribe(self, fp):
        pass


class TTSPlugin(GenericPlugin):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def say(self, phrase, *args):
        pass

    def mp3_to_wave(self, filename):
        mf = mad.MadFile(filename)
        with tempfile.SpooledTemporaryFile() as f:
            wav = wave.open(f, mode='wb')
            wav.setframerate(mf.samplerate())
            wav.setnchannels(1 if mf.mode() == mad.MODE_SINGLE_CHANNEL else 2)
            # 4L is the sample width of 32 bit audio
            wav.setsampwidth(4)
            frame = mf.read()
            while frame is not None:
                wav.writeframes(frame)
                frame = mf.read()
            wav.close()
            f.seek(0)
            data = f.read()
        return data
