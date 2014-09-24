# -*- coding: utf-8-*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    is_available - returns True if the platform supports this implementation
"""
import os
import platform
import re
import sys
import tempfile
import subprocess
import pipes
import logging
from abc import ABCMeta, abstractmethod
from distutils.spawn import find_executable

import yaml
import argparse

import wave
try:
    import mad
    import gtts
except ImportError:
    pass

class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta
    
    @classmethod
    @abstractmethod
    def is_available(cls):
        return (find_executable('aplay') is not None)

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def say(self, phrase, *args):
        pass

    def play(self, filename):
        # FIXME: Use platform-independent audio-output here
        # See issue jasperproject/jasper-client#188
        cmd = ['aplay', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)

class AbstractMp3TTSEngine(AbstractTTSEngine):
    """
    Generic class that implements the 'play' method for mp3 files
    """
    @classmethod
    def is_available(cls):
        return (super(AbstractMp3TTSEngine, cls).is_available() and 'mad' in sys.modules.keys())

    def play_mp3(self, filename):
        mf = mad.MadFile(filename)
        with tempfile.NamedTemporaryFile(suffix='.wav') as f:
            wav = wave.open(f, mode='wb')
            wav.setframerate(mf.samplerate())
            wav.setnchannels(1 if mf.mode() == mad.MODE_SINGLE_CHANNEL else 2)
            wav.setsampwidth(4L) # width of 32 bit audio
            frame = mf.read()
            while frame is not None:
                wav.writeframes(frame)
                frame = mf.read()
            wav.close()
            self.play(f.name)

class DummyTTS(AbstractTTSEngine):
    """
    Dummy TTS engine that logs phrases with INFO level instead of synthesizing
    speech.
    """

    SLUG = "dummy-tts"

    @classmethod
    def is_available(cls):
        return True

    def say(self, phrase):
        self._logger.info(phrase)
    
    def play(self, filename):
        self._logger.debug("Playback of file '%s' requested")
        pass

class EspeakTTS(AbstractTTSEngine):
    """
    Uses the eSpeak speech synthesizer included in the Jasper disk image
    Requires espeak to be available
    """

    SLUG = "espeak-tts"

    def __init__(self, voice='default+m3', pitch_adjustment=40, words_per_minute=160):
        super(self.__class__, self).__init__()
        self.voice = voice
        self.pitch_adjustment = pitch_adjustment
        self.words_per_minute = words_per_minute

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and find_executable('espeak') is not None)

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['espeak', '-v', self.voice,
                         '-p', self.pitch_adjustment,
                         '-s', self.words_per_minute,
                         '-w', fname,
                         phrase]
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)

class FestivalTTS(AbstractTTSEngine):
    """
    Uses the festival speech synthesizer
    Requires festival (text2wave) to be available
    """

    SLUG = 'festival-tts'

    @classmethod
    def is_available(cls):
        if super(cls, cls).is_available() and find_executable('text2wave') is not None and find_executable('festival') is not None:
            logger = logging.getLogger(__name__)
            cmd = ['festival', '--pipe']
            with tempfile.SpooledTemporaryFile() as out_f:
                with tempfile.SpooledTemporaryFile() as in_f:
                    logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
                    subprocess.call(cmd, stdin=in_f, stdout=out_f, stderr=out_f)
                    out_f.seek(0)
                    output = out_f.read().strip()
                    if output:
                        logger.debug("Output was: '%s'", output)
                    return ('No default voice found' not in output)
        return False

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        cmd = ['text2wave']
        with tempfile.NamedTemporaryFile(suffix='.wav') as out_f:
            with tempfile.SpooledTemporaryFile() as in_f:
                in_f.write(phrase)
                in_f.seek(0)
                with tempfile.SpooledTemporaryFile() as err_f:
                    self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
                    subprocess.call(cmd, stdin=in_f, stdout=out_f, stderr=err_f)
                    err_f.seek(0)
                    output = err_f.read()
                    if output:
                        self._logger.debug("Output was: '%s'", output)
            self.play(out_f.name)

class MacOSXTTS(AbstractTTSEngine):
    """
    Uses the OS X built-in 'say' command
    """

    SLUG = "osx-tts"

    @classmethod
    def is_available(cls):
        return (platform.system() == 'darwin' and find_executable('say') is not None and find_executable('afplay') is not None)

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        cmd = ['say', str(phrase)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)

    def play(self, filename):
        cmd = ['afplay', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)

class PicoTTS(AbstractTTSEngine):
    """
    Uses the svox-pico-tts speech synthesizer
    Requires pico2wave to be available
    """

    SLUG = "pico-tts"

    def __init__(self, language="en-US"):
        super(self.__class__, self).__init__()
        self.language = language

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and find_executable('pico2wave') is not None)

    @property
    def languages(self):
        cmd = ['pico2wave', '-l', 'NULL',
                            '-w', os.devnull,
                            'NULL']
        with tempfile.SpooledTemporaryFile() as f:
            subprocess.call(cmd, stderr=f)
            f.seek(0)
            output = f.read()
        pattern = re.compile(r'Unknown language: NULL\nValid languages:\n((?:[a-z]{2}-[A-Z]{2}\n)+)')
        matchobj = pattern.match(output)
        if not matchobj:
            raise RuntimeError("pico2wave: valid languages not detected")
        langs = matchobj.group(1).split()
        return langs

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['pico2wave', '--wave', fname]
        if self.language not in self.languages:
                raise ValueError("Language '%s' not supported by '%s'", self.language, self.SLUG)
        cmd.extend(['-l', self.language])
        cmd.append(phrase)
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)

class GoogleTTS(AbstractMp3TTSEngine):
    """
    Uses the Google TTS online translator
    Requires pymad and gTTS to be available
    """

    SLUG = "google-tts"

    def __init__(self, language='en'):
        super(self.__class__, self).__init__()
        self.language = language

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and 'gtts' in sys.modules.keys())

    @property
    def languages(self):
        langs = ['af', 'sq', 'ar', 'hy', 'ca', 'zh-CN', 'zh-TW', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'fi', 'fr', 'de',
                 'el', 'ht', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'ko', 'la', 'lv', 'mk', 'no', 'pl', 'pt', 'ro', 'ru',
                 'sr', 'sk', 'es', 'sw', 'sv', 'ta', 'th', 'tr', 'vi', 'cy']
        return langs

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        if self.language not in self.languages:
            raise ValueError("Language '%s' not supported by '%s'", self.language, self.SLUG)
        tts = gtts.gTTS(text=phrase, lang=self.language)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self.play_mp3(tmpfile)
        os.remove(tmpfile)

def get_default_engine_slug():
    return 'osx-tts' if platform.system() == 'darwin' else 'espeak-tts'

def get_engine_by_slug(slug=None):
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """
    
    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No TTS engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple TTS engines found for slug '%s'. This is most certainly a bug." % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError("TTS engine '%s' is not available (due to missing dependencies, missing dependencies, etc.)" % slug)
        return engine

def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in list(get_subclasses(AbstractTTSEngine)) if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper TTS module')
    parser.add_argument('--debug', action='store_true', help='Show debug messages')
    args = parser.parse_args()

    logging.basicConfig()
    if args.debug:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
    
    engines = get_engines()
    available_engines = []
    for engine in get_engines():
        if engine.is_available():
            available_engines.append(engine)
    print("Available TTS engines:")
    for i, engine in enumerate(available_engines, start=1):
        print("%d. %s" % (i, engine.SLUG))
    
    print("")
    print("Disabled TTS engines:")
    for i, engine in enumerate(list(set(engines).difference(set(available_engines))), start=1):
        print("%d. %s" % (i, engine.SLUG))

    print("")
    for i, engine in enumerate(available_engines, start=1):
        print("%d. Testing engine '%s'..." % (i, engine.SLUG))
        engine().say("This is a test.")
    print("Done.")
